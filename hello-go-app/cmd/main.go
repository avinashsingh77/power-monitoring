package main

import (
	"fmt"
	"hello-go-app/pkg/hello"
	"runtime"
	"time"
)

// cpuIntensiveWork simulates a CPU-bound task.
func cpuIntensiveWork() {
	for {
		// A tight loop to consume CPU.
		// The values can be tuned to make it more or less intensive.
		for i := 0; i < 2000000; i++ {
			_ = i * i
		}
		// Sleep for a short period to avoid pegging the CPU at 100% constantly
		time.Sleep(50 * time.Millisecond)
	}
}

func main() {
	// Use a number of goroutines equal to the number of available CPU cores
	// to generate a significant and consistent load.
	numWorkers := runtime.NumCPU()
	fmt.Printf("Starting %d CPU-intensive worker goroutines to increase resource consumption...\n", numWorkers)
	for i := 0; i < numWorkers; i++ {
		go cpuIntensiveWork()
	}

	// The memory leak code remains commented out for reference.
	// var memoryLeaker []string
	/*
		// Memory leak simulation
		go func() {
			for {
				// Allocate memory without releasing it
				data := make([]string, 100000)
				for i := range data {
					data[i] = fmt.Sprintf("leaking memory %d", i)
				}
				memoryLeaker = append(memoryLeaker, data...)

				// Print current memory stats
				var m runtime.MemStats
				runtime.ReadMemStats(&m)
				fmt.Printf("Allocated memory: %v MB\n", m.Alloc/1024/1024)

				time.Sleep(100 * time.Millisecond)
			}
		}()
	*/

	// The main loop can now do minimal work in the background.
	go func() {
		for {
			fmt.Println(hello.SayHello())
			time.Sleep(5 * time.Second)
		}
	}()

	// Keep the main goroutine running indefinitely to allow workers to run.
	select {}
}
