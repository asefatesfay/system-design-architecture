package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sync/atomic"
	"time"
)

// BAD: Aggressive retries without backoff or circuit breaker

var (
	requestCount   int64
	failureRate    = 0.7 // 70% of requests fail (simulating degraded service)
	serviceHealthy = true
)

// Simulated external service that's struggling
func unreliableServiceHandler(w http.ResponseWriter, r *http.Request) {
	atomic.AddInt64(&requestCount, 1)
	count := atomic.LoadInt64(&requestCount)

	// Simulate high failure rate when under heavy load
	if rand.Float64() < failureRate {
		log.Printf("❌ Service request #%d FAILED (service overloaded)", count)
		http.Error(w, "Service unavailable", http.StatusServiceUnavailable)
		return
	}

	log.Printf("✅ Service request #%d succeeded", count)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "success",
		"data":   "Response data",
	})
}

// ANTIPATTERN: Aggressive retry without backoff
func callServiceWithBadRetry() (string, error) {
	maxRetries := 5
	var lastErr error

	for attempt := 1; attempt <= maxRetries; attempt++ {
		log.Printf("🔄 Attempt %d/%d (no backoff)", attempt, maxRetries)

		resp, err := http.Get("http://localhost:9090/api/data")
		if err != nil {
			lastErr = err
			// ANTIPATTERN: Retry immediately without any delay!
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			return "Success", nil
		}

		lastErr = fmt.Errorf("status: %d", resp.StatusCode)
		// ANTIPATTERN: Fixed 100ms delay (no exponential backoff)
		time.Sleep(100 * time.Millisecond)
	}

	return "", fmt.Errorf("failed after %d retries: %v", maxRetries, lastErr)
}

func clientHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	result, err := callServiceWithBadRetry()
	if err != nil {
		log.Printf("❌ Client request failed after %v: %v", time.Since(start), err)
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}

	duration := time.Since(start)
	log.Printf("✅ Client request succeeded after %v", duration)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"result":   result,
		"duration": duration.String(),
	})
}

func statsHandler(w http.ResponseWriter, r *http.Request) {
	count := atomic.LoadInt64(&requestCount)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"total_requests": count,
		"failure_rate":   failureRate,
	})
}

func main() {
	// Unreliable service
	go func() {
		mux := http.NewServeMux()
		mux.HandleFunc("/api/data", unreliableServiceHandler)
		log.Fatal(http.ListenAndServe(":9090", mux))
	}()

	// Give service time to start
	time.Sleep(500 * time.Millisecond)

	// Client service
	http.HandleFunc("/call", clientHandler)
	http.HandleFunc("/stats", statsHandler)

	fmt.Println("❌ BAD: Retry storm demo starting")
	fmt.Println("Unreliable service: http://localhost:9090")
	fmt.Println("Client service: http://localhost:8090")
	fmt.Println("\nThis demonstrates RETRY STORM antipattern:")
	fmt.Println("- No exponential backoff")
	fmt.Println("- No jitter")
	fmt.Println("- No circuit breaker")
	fmt.Println("- Hammers failing service")
	fmt.Println("\nTry: curl http://localhost:8090/call")
	fmt.Println("Try: curl http://localhost:8090/stats")
	fmt.Println("\nWatch logs - aggressive retries prevent service recovery!")

	log.Fatal(http.ListenAndServe(":8090", nil))
}
