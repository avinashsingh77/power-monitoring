package main

import (
	"fmt"
	"hello-go-app/pkg/hello"
	"runtime"
	"time"
)

// Declare the global variable to store the leaking memory
// var memoryLeaker []string

func main() {
	for {
		fmt.Println(hello.SayHello())

		// Simulate a long-running process
		time.Sleep(1 * time.Second)

		/*
			// Start CPU-intensive goroutine
			go func() {
				for {
					// Perform CPU-intensive calculations
					for i := 0; i < 1000000; i++ {
						_ = i * i * i
					}
				}
			}()
		*/

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

		// Keep main goroutine running
		// select {}

	}
}
