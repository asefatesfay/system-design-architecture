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

// GOOD: Optimized I/O - single JOIN query

type Order struct {
	ID         int       `json:"id"`
	CustomerID int       `json:"customer_id"`
	Total      float64   `json:"total"`
	CreatedAt  time.Time `json:"created_at"`
	Customer   *Customer `json:"customer"`
}

type Customer struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
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

// GOOD: Single optimized query with JOIN
// Fetches all data in ONE database round trip
func getOrders() ([]Order, error) {
	start := time.Now()

	// Single query with JOIN - gets everything at once!
	query := `
		SELECT 
			o.id, o.customer_id, o.total, o.created_at,
			c.id, c.name, c.email
		FROM orders o
		INNER JOIN customers c ON o.customer_id = c.id
		LIMIT 100
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var orders []Order
	for rows.Next() {
		var order Order
		var customer Customer

		// Scan both order and customer data in one go
		if err := rows.Scan(
&order.ID, &order.CustomerID, &order.Total, &order.CreatedAt,
			&customer.ID, &customer.Name, &customer.Email,
		); err != nil {
			return nil, err
		}

		order.Customer = &customer
		orders = append(orders, order)
	}

	duration := time.Since(start)
	log.Printf("✅ GOOD: Fetched %d orders with 1 JOIN query in %v", len(orders), duration)

	return orders, nil
}

func ordersHandler(w http.ResponseWriter, r *http.Request) {
	orders, err := getOrders()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(orders)
}

func main() {
	http.HandleFunc("/orders", ordersHandler)

	fmt.Println("✅ GOOD: Server starting on :8085")
	fmt.Println("This server demonstrates OPTIMIZED I/O:")
	fmt.Println("- Makes 1 JOIN query to get all data")
	fmt.Println("- No N+1 problem")
	fmt.Println("- Total queries = 1 (regardless of order count)")
	fmt.Println("\nFor 100 orders = only 1 database round trip!")
	fmt.Println("\nTry: curl http://localhost:8085/orders")
	fmt.Println("Compare with bad version - 100x fewer queries!")

	log.Fatal(http.ListenAndServe(":8085", nil))
}
