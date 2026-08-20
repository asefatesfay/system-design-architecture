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

// BAD: Chatty I/O - N+1 query problem

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

// BAD: Makes N+1 database queries
// 1 query for orders + N queries for each customer
func getOrders() ([]Order, error) {
	start := time.Now()

	// Query 1: Get all orders (1 query)
	rows, err := db.Query("SELECT id, customer_id, total, created_at FROM orders LIMIT 100")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var orders []Order
	for rows.Next() {
		var order Order
		if err := rows.Scan(&order.ID, &order.CustomerID, &order.Total, &order.CreatedAt); err != nil {
			return nil, err
		}
		orders = append(orders, order)
	}

	// Query 2-N: Get customer for EACH order (N queries)
	// THIS IS THE PROBLEM!
	for i := range orders {
		customer, err := getCustomer(orders[i].CustomerID)
		if err != nil {
			log.Printf("Error fetching customer: %v", err)
			continue
		}
		orders[i].Customer = customer
	}

	duration := time.Since(start)
	log.Printf("❌ BAD: Fetched %d orders with N+1 queries in %v", len(orders), duration)

	return orders, nil
}

// This function is called N times - once per order
func getCustomer(customerID int) (*Customer, error) {
	var customer Customer
	err := db.QueryRow(
"SELECT id, name, email FROM customers WHERE id = $1",
customerID,
).Scan(&customer.ID, &customer.Name, &customer.Email)

	if err != nil {
		return nil, err
	}

	return &customer, nil
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

	fmt.Println("❌ BAD: Server starting on :8084")
	fmt.Println("This server demonstrates CHATTY I/O (N+1 problem):")
	fmt.Println("- Makes 1 query for orders")
	fmt.Println("- Makes N additional queries (1 per order) for customer data")
	fmt.Println("- Total queries = 1 + N")
	fmt.Println("\nFor 100 orders = 101 database round trips!")
	fmt.Println("\nTry: curl http://localhost:8084/orders")
	fmt.Println("Watch the logs for query count")

	log.Fatal(http.ListenAndServe(":8084", nil))
}
