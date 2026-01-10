package benchmarks

import (
"context"
"database/sql"
"testing"
"time"
_ "github.com/lib/pq"
"github.com/redis/go-redis/v9"
)

var testDB *sql.DB
var redisClient *redis.Client

func setupDatabase() error {
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

func setupRedis() error {
	redisClient = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})
	return redisClient.Ping(context.Background()).Err()
}

func BenchmarkNoCache_DirectDB(b *testing.B) {
	if err := setupDatabase(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var name string
		var email string
		testDB.QueryRow("SELECT name, email FROM users WHERE id = $1", 1).Scan(&name, &email)
	}
}

func BenchmarkWithCache_CacheMiss(b *testing.B) {
	if err := setupDatabase(); err != nil {
		b.Skip("Database not available:", err)
	}
	defer testDB.Close()

	if err := setupRedis(); err != nil {
		b.Skip("Redis not available:", err)
	}
	defer redisClient.Close()

	ctx := context.Background()
	redisClient.FlushDB(ctx)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cacheKey := "user:1"
		val, err := redisClient.Get(ctx, cacheKey).Result()
		
		if err == redis.Nil {
			var name, email string
			testDB.QueryRow("SELECT name, email FROM users WHERE id = $1", 1).Scan(&name, &email)
			redisClient.Set(ctx, cacheKey, name+":"+email, 5*time.Minute)
		} else if err == nil {
			_ = val
		}
		
		redisClient.Del(ctx, cacheKey)
	}
}

func BenchmarkWithCache_CacheHit(b *testing.B) {
	if err := setupRedis(); err != nil {
		b.Skip("Redis not available:", err)
	}
	defer redisClient.Close()

	ctx := context.Background()
	cacheKey := "user:1"
	redisClient.Set(ctx, cacheKey, "John:john@example.com", 5*time.Minute)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		val, err := redisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			_ = val
		}
	}
}
