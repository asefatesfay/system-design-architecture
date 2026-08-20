package benchmarks

import (
"database/sql"
"testing"
_ "github.com/lib/pq"
)

var testDB *sql.DB

func setupTestDB() error {
	var err error
	connStr := "host=localhost port=5432 user=postgres password=postgres dbname=performance sslmode=disable"
	testDB, err = sql.Open("postgres", connStr)
	if err != nil {
		return err
	}
	testDB.SetMaxOpenConns(25)
	testDB.SetMaxIdleConns(25)
	return testDB.Ping()
}

func BenchmarkBusyDB_DatabaseAggregation(b *testing.B) {
	if err := setupTestDB(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var totalSales float64
		var orderCount int
		var avgOrderValue float64

		err := testDB.QueryRow(`
			SELECT 
				SUM(total) as total_sales,
				COUNT(*) as order_count,
				AVG(total) as avg_order_value
			FROM orders
			WHERE user_id = $1
		`, 1).Scan(&totalSales, &orderCount, &avgOrderValue)

		if err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkOptimizedDB_ApplicationProcessing(b *testing.B) {
	if err := setupTestDB(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rows, err := testDB.Query("SELECT total FROM orders WHERE user_id = $1", 1)
		if err != nil {
			b.Fatal(err)
		}

		var totalSales float64
		var orderCount int

		for rows.Next() {
			var total float64
			rows.Scan(&total)
			totalSales += total
			orderCount++
		}
		rows.Close()

		var avgOrderValue float64
		if orderCount > 0 {
			avgOrderValue = totalSales / float64(orderCount)
		}

		_ = totalSales
		_ = orderCount
		_ = avgOrderValue
	}
}
