package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"time"

	_ "github.com/lib/pq"
)

// BAD: Creating expensive objects on every request

type User struct {
	ID    int    `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
}

// BAD: Handler creates new DB connection on every request
func getUserHandler(w http.ResponseWriter, r *http.Request) {
	// ANTIPATTERN: Opening a new database connection for each request
	db, err := sql.Open("postgres", "postgres://testuser:testpass@localhost:5432/perftest?sslmode=disable")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer db.Close()

	// ANTIPATTERN: Creating new HTTP client every time
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Simulate calling external API
	resp, err := client.Get("https://jsonplaceholder.typicode.com/users/1")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// ANTIPATTERN: Compiling regex on every request
	emailRegex, err := regexp.Compile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var user User
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Validate email with compiled regex
	if !emailRegex.MatchString(user.Email) {
		http.Error(w, "Invalid email", http.StatusBadRequest)
		return
	}

	// Try to save to database
	_, err = db.Exec("INSERT INTO users (email, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
		user.Email, user.Name)
	if err != nil {
		log.Printf("DB error: %v", err)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func main() {
	// Note: This setup doesn't create the table, just demonstrates the antipattern
	http.HandleFunc("/user", getUserHandler)

	fmt.Println("❌ BAD: Server starting on :8080")
	fmt.Println("This server demonstrates IMPROPER INSTANTIATION antipattern:")
	fmt.Println("- Creates new DB connection per request")
	fmt.Println("- Creates new HTTP client per request")
	fmt.Println("- Compiles regex per request")
	fmt.Println("\nTry: curl http://localhost:8080/user")
	fmt.Println("\nWatch the performance degrade under load!")

	log.Fatal(http.ListenAndServe(":8080", nil))
}
