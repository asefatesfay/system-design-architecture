package main

import (
"database/sql"
"encoding/json"
"fmt"
"log"
"net/http"
"time"

_ "github.com/lib/pq"
)

// BAD: No Caching - every request hits the database

type Product struct {
	ID          int     `json:"id"`
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	Stock       int     `json:"stock"`
}

var db *sql.DB

func init() {
	var err error
	connStr := "host=localhost port=5432 user=postgres password=postgres dbname=performance sslmode=disable"
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)
}

// BAD: Always queries database, no caching
func getProduct(id int) (*Product, error) {
	start := time.Now()

	var product Product
	err := db.QueryRow(`
		SELECT id, name, description, price, stock
		FROM products WHERE id = $1
	`, id).Scan(&product.ID, &product.Name, &product.Description, &product.Price, &product.Stock)

	if err != nil {
		return nil, err
	}

	duration := time.Since(start)
	log.Printf("❌ BAD: Database query took %v for product %d", duration, id)

	return &product, nil
}

func productHandler(w http.ResponseWriter, r *http.Request) {
	// Always hits database - even for frequently accessed products
	product, err := getProduct(1)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(product)
}

func main() {
	http.HandleFunc("/product", productHandler)

	fmt.Println("❌ BAD: Server starting on :8086")
	fmt.Println("This server demonstrates NO CACHING:")
	fmt.Println("- Every request queries the database")
	fmt.Println("- No cache layer")
	fmt.Println("- Database becomes bottleneck under load")
	fmt.Println("\nTry: curl http://localhost:8086/product")
	fmt.Println("Run multiple times - each hits database!")

	log.Fatal(http.ListenAndServe(":8086", nil))
}
