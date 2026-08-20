package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"sync"
	"time"

	_ "github.com/lib/pq"
)

// GOOD: Reusing expensive objects

type User struct {
	ID    int    `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
}

// GOOD: Package-level HTTP client (reuses connections)
var httpClient = &http.Client{
	Timeout: 10 * time.Second,
	Transport: &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 100,
		IdleConnTimeout:     90 * time.Second,
	},
}

// GOOD: Pre-compiled regex
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

// GOOD: Database connection pool (initialized once)
var (
	db     *sql.DB
	dbOnce sync.Once
)

func initDB() {
	dbOnce.Do(func() {
		var err error
		db, err = sql.Open("postgres", "postgres://testuser:testpass@localhost:5432/perftest?sslmode=disable")
		if err != nil {
			log.Fatal(err)
		}

		// Configure connection pool
		db.SetMaxOpenConns(25)
		db.SetMaxIdleConns(25)
		db.SetConnMaxLifetime(5 * time.Minute)

		// Verify connection
		if err = db.Ping(); err != nil {
			log.Fatal(err)
		}

		// Create table if not exists
		_, err = db.Exec(`
			CREATE TABLE IF NOT EXISTS users (
				id SERIAL PRIMARY KEY,
				email VARCHAR(255) UNIQUE NOT NULL,
				name VARCHAR(255) NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		`)
		if err != nil {
			log.Fatal(err)
		}

		log.Println("✅ Database connection pool initialized")
	})
}

// GOOD: Handler reuses all expensive objects
func getUserHandler(w http.ResponseWriter, r *http.Request) {
	// Use pre-initialized HTTP client
	resp, err := httpClient.Get("https://jsonplaceholder.typicode.com/users/1")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	var user User
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Use pre-compiled regex
	if !emailRegex.MatchString(user.Email) {
		http.Error(w, "Invalid email", http.StatusBadRequest)
		return
	}

	// Use connection from pool
	_, err = db.Exec("INSERT INTO users (email, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
		user.Email, user.Name)
	if err != nil {
		log.Printf("DB error: %v", err)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func main() {
	// Initialize database connection pool once at startup
	initDB()
	defer db.Close()

	http.HandleFunc("/user", getUserHandler)

	fmt.Println("✅ GOOD: Server starting on :8081")
	fmt.Println("This server demonstrates PROPER INSTANTIATION:")
	fmt.Println("- Reuses DB connection pool")
	fmt.Println("- Reuses HTTP client with connection pooling")
	fmt.Println("- Uses pre-compiled regex")
	fmt.Println("\nTry: curl http://localhost:8081/user")
	fmt.Println("\nMuch better performance under load!")

	log.Fatal(http.ListenAndServe(":8081", nil))
}
