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

type SalesReport struct {
	TotalRevenue float64 `json:"total_revenue"`
	OrderCount   int     `json:"order_count"`
	AvgOrderSize float64 `json:"avg_order_size"`
}

type Order struct {
	Total float64
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

func getSalesReport() (*SalesReport, error) {
	start := time.Now()
	rows, err := db.Query(`SELECT total FROM orders WHERE created_at > NOW() - INTERVAL '30 days'`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var orders []Order
	for rows.Next() {
		var order Order
		if err := rows.Scan(&order.Total); err != nil {
			return nil, err
		}
		orders = append(orders, order)
	}

	var totalRevenue float64
	for _, order := range orders {
		totalRevenue += order.Total
	}

	report := &SalesReport{
		TotalRevenue: totalRevenue,
		OrderCount:   len(orders),
		AvgOrderSize: totalRevenue / float64(len(orders)),
	}

	log.Printf("✅ GOOD: App-level processing took %v", time.Since(start))
	return report, nil
}

func reportHandler(w http.ResponseWriter, r *http.Request) {
	report, err := getSalesReport()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(report)
}

func main() {
	http.HandleFunc("/report", reportHandler)
	fmt.Println("✅ GOOD: Server on :8089 - app-level processing")
	log.Fatal(http.ListenAndServe(":8089", nil))
}
