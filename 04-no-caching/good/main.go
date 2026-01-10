package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
)

type Product struct {
	ID          int     `json:"id"`
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	Stock       int     `json:"stock"`
}

var (
	db          *sql.DB
	redisClient *redis.Client
	ctx         = context.Background()
)

func init() {
	var err error
	connStr := "host=localhost port=5432 user=postgres password=postgres dbname=performance sslmode=disable"
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)

	redisClient = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
		DB:   0,
	})
}

func getProduct(id int) (*Product, error) {
	cacheKey := fmt.Sprintf("product:%d", id)

	cachedData, err := redisClient.Get(ctx, cacheKey).Result()
	if err == nil {
		var product Product
		if err := json.Unmarshal([]byte(cachedData), &product); err == nil {
			log.Printf("✅ Cache HIT for product %d", id)
			return &product, nil
		}
	}

	log.Printf("⚠️  Cache MISS - querying database")
	start := time.Now()

	var product Product
	err = db.QueryRow(`SELECT id, name, description, price, stock FROM products WHERE id = $1`, id).Scan(
		&product.ID, &product.Name, &product.Description, &product.Price, &product.Stock)

	if err != nil {
		return nil, err
	}

	log.Printf("Database query took %v", time.Since(start))

	productJSON, _ := json.Marshal(product)
	redisClient.Set(ctx, cacheKey, productJSON, 5*time.Minute)

	return &product, nil
}

func productHandler(w http.ResponseWriter, r *http.Request) {
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
	fmt.Println("✅ GOOD: Server on :8087 with Redis caching")
	log.Fatal(http.ListenAndServe(":8087", nil))
}
