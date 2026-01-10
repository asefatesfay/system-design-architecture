package main

import (
"fmt"
"log"
"math"
"math/rand"
"net/http"
"sync"
"time"
)

type CircuitBreaker struct {
	failures    int
	lastFailure time.Time
	state       string
	mu          sync.Mutex
}

func (cb *CircuitBreaker) Call(fn func() error) error {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	if cb.state == "open" && time.Since(cb.lastFailure) < 30*time.Second {
		return fmt.Errorf("circuit breaker open")
	}

	if err := fn(); err != nil {
		cb.failures++
		cb.lastFailure = time.Now()
		if cb.failures >= 3 {
			cb.state = "open"
			log.Println("⚠️  Circuit breaker opened")
		}
		return err
	}

	cb.failures = 0
	cb.state = "closed"
	return nil
}

var (
cb           = &CircuitBreaker{state: "closed"}
	failureCount = 0
)

func unreliableService(w http.ResponseWriter, r *http.Request) {
	failureCount++
	if failureCount%3 == 0 {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Success"))
	} else {
		w.WriteHeader(http.StatusServiceUnavailable)
		w.Write([]byte("Service Unavailable"))
	}
}

func exponentialBackoff(attempt int) time.Duration {
	base := 100 * time.Millisecond
	delay := base * time.Duration(math.Pow(2, float64(attempt-1)))
	jitter := time.Duration(rand.Float64()*50) * time.Millisecond
	return delay + jitter
}

func callServiceWithCircuitBreaker() error {
	maxRetries := 5
	for i := 0; i < maxRetries; i++ {
		err := cb.Call(func() error {
			resp, err := http.Get("http://localhost:9001/api")
			if err != nil || resp.StatusCode != http.StatusOK {
				return fmt.Errorf("service unavailable")
			}
			return nil
		})
		
		if err == nil {
			log.Printf("✅ Success on attempt %d", i+1)
			return nil
		}
		
		if err.Error() == "circuit breaker open" {
			log.Printf("⚡ Circuit breaker open, failing fast")
			return err
		}
		
		if i < maxRetries-1 {
			backoff := exponentialBackoff(i + 1)
			log.Printf("⏳ Backing off for %v", backoff)
			time.Sleep(backoff)
		}
	}
	return fmt.Errorf("failed after %d retries", maxRetries)
}

func clientHandler(w http.ResponseWriter, r *http.Request) {
	if err := callServiceWithCircuitBreaker(); err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	w.Write([]byte("Success"))
}

func main() {
	go func() {
		http.HandleFunc("/api", unreliableService)
		log.Fatal(http.ListenAndServe(":9001", nil))
	}()

	time.Sleep(1 * time.Second)

	http.HandleFunc("/call", clientHandler)
	fmt.Println("✅ GOOD: Server on :8091 - circuit breaker + exponential backoff")
	log.Fatal(http.ListenAndServe(":8091", nil))
}
