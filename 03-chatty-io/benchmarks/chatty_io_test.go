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

func BenchmarkChattyIO_NPlus1(b *testing.B) {
	if err := setupTestDB(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rows, err := testDB.Query("SELECT id, customer_id FROM orders LIMIT 10")
		if err != nil {
			b.Fatal(err)
		}

		type Order struct {
			ID         int
			CustomerID int
		}
		var orders []Order

		for rows.Next() {
			var o Order
			rows.Scan(&o.ID, &o.CustomerID)
			orders = append(orders, o)
		}
		rows.Close()

		for _, order := range orders {
			var name string
			testDB.QueryRow("SELECT name FROM customers WHERE id = $1", order.CustomerID).Scan(&name)
		}
	}
}

func BenchmarkOptimizedIO_Join(b *testing.B) {
	if err := setupTestDB(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rows, err := testDB.Query(`
			SELECT o.id, o.customer_id, c.name
			FROM orders o
			INNER JOIN customers c ON o.customer_id = c.id
			LIMIT 10
		`)
		if err != nil {
			b.Fatal(err)
		}

		for rows.Next() {
			var id, customerID int
			var name string
			rows.Scan(&id, &customerID, &name)
		}
		rows.Close()
	}
}
