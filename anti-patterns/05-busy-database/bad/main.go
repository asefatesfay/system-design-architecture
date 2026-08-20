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
	var report SalesReport
	err := db.QueryRow(`
		SELECT 
			SUM(total) as total_revenue,
			COUNT(*) as order_count,
			AVG(total) as avg_order_size
		FROM orders
		WHERE created_at > NOW() - INTERVAL '30 days'
	`).Scan(&report.TotalRevenue, &report.OrderCount, &report.AvgOrderSize)
	if err != nil {
		return nil, err
	}
	log.Printf("❌ BAD: Database aggregation took %v", time.Since(start))
	return &report, nil
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
	fmt.Println("❌ BAD: Server on :8088 - heavy DB aggregations")
	log.Fatal(http.ListenAndServe(":8088", nil))
}
