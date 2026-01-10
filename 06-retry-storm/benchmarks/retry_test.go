package benchmarks

import (
"errors"
"math"
"math/rand"
"testing"
"time"
)

var failureRate = 0.8

func simulateUnstableService() error {
	if rand.Float64() < failureRate {
		return errors.New("service unavailable")
	}
	return nil
}

func BenchmarkRetryStorm_AggressiveRetry(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		maxRetries := 10
		for attempt := 0; attempt < maxRetries; attempt++ {
			err := simulateUnstableService()
			if err == nil {
				break
			}
		}
	}
}

func exponentialBackoff(attempt int) time.Duration {
	baseDelay := 100 * time.Millisecond
	maxDelay := 10 * time.Second
	
	delay := time.Duration(float64(baseDelay) * math.Pow(2, float64(attempt)))
	if delay > maxDelay {
		delay = maxDelay
	}
	
	jitter := time.Duration(rand.Int63n(int64(delay) / 2))
	return delay + jitter
}

type CircuitBreaker struct {
	failureThreshold int
	timeout          time.Duration
	failures         int
	lastFailureTime  time.Time
	state            string
}

func NewCircuitBreaker() *CircuitBreaker {
	return &CircuitBreaker{
		failureThreshold: 5,
		timeout:          5 * time.Second,
		state:            "closed",
	}
}

func (cb *CircuitBreaker) Call(fn func() error) error {
	if cb.state == "open" {
		if time.Since(cb.lastFailureTime) > cb.timeout {
			cb.state = "half-open"
			cb.failures = 0
		} else {
			return errors.New("circuit breaker open")
		}
	}

	err := fn()
	if err != nil {
		cb.failures++
		cb.lastFailureTime = time.Now()
		if cb.failures >= cb.failureThreshold {
			cb.state = "open"
		}
		return err
	}

	if cb.state == "half-open" {
		cb.state = "closed"
	}
	cb.failures = 0
	return nil
}

func BenchmarkOptimizedRetry_CircuitBreaker(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cb := NewCircuitBreaker()
		maxRetries := 3

		for attempt := 0; attempt < maxRetries; attempt++ {
			err := cb.Call(simulateUnstableService)
			if err == nil {
				break
			}
			
			if attempt < maxRetries-1 {
				backoff := exponentialBackoff(attempt)
				time.Sleep(backoff)
			}
		}
	}
}
