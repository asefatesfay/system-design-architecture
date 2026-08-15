/*
 * JavaScript: Page View Counter - Race Condition Demo
 * ====================================================
 * Shows:
 * 1. Why single-threaded JS usually doesn't have races
 * 2. Worker threads CAN cause races
 * 3. Using Atomics for shared memory
 * 4. Why async/await doesn't need locks
 *
 * Note: Requires Node.js 12+ for Worker threads
 */

const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

console.log("================================================================================");
console.log("          JAVASCRIPT: RACE CONDITION DEMONSTRATION");
console.log("================================================================================");

// ============================================================================
// Version 1: Single-threaded (NO RACE - event loop is sequential)
// ============================================================================
class PageViewCounterSingleThreaded {
    constructor() {
        this.views = 0;
    }

    increment() {
        // Even with async operations, no race in single thread
        const temp = this.views;
        this.views = temp + 1;
    }

    getViews() {
        return this.views;
    }
}

async function demonstrateSingleThreaded() {
    console.log("\n1. SINGLE-THREADED VERSION (No Race Possible)");
    console.log("--------------------------------------------------------------------------------");
    console.log("JavaScript's event loop is single-threaded, so no race conditions by default");

    const counter = new PageViewCounterSingleThreaded();

    // Even with 1000 async operations, they run sequentially
    const promises = [];
    for (let i = 0; i < 1000; i++) {
        promises.push(
            new Promise(resolve => {
                counter.increment();
                resolve();
            })
        );
    }

    await Promise.all(promises);

    console.log(`Expected: 1000`);
    console.log(`Actual:   ${counter.getViews()}`);
    console.log(`Status:   ✅ Correct! (Event loop is sequential)`);
}

// ============================================================================
// Version 2: Worker Threads WITHOUT synchronization (BROKEN)
// ============================================================================
function demonstrateWorkerThreadsBroken() {
    return new Promise((resolve) => {
        console.log("\n2. WORKER THREADS - BROKEN (No Synchronization)");
        console.log("--------------------------------------------------------------------------------");
        console.log("With SharedArrayBuffer, worker threads CAN have race conditions!");

        // Shared memory between workers
        const sharedBuffer = new SharedArrayBuffer(4); // 4 bytes = 1 int32
        const sharedArray = new Int32Array(sharedBuffer);
        sharedArray[0] = 0; // Initial value

        let workersCompleted = 0;
        const totalWorkers = 10;

        // Create 10 workers, each incrementing 100 times
        for (let i = 0; i < totalWorkers; i++) {
            const worker = new Worker(__filename, {
                workerData: { sharedBuffer, iterations: 100, useAtomic: false }
            });

            worker.on('exit', () => {
                workersCompleted++;
                if (workersCompleted === totalWorkers) {
                    console.log(`Expected: 1000 (10 workers × 100 increments)`);
                    console.log(`Actual:   ${sharedArray[0]}`);
                    console.log(`Lost:     ${1000 - sharedArray[0]} increments`);
                    console.log(`Status:   ${sharedArray[0] === 1000 ? '✅ Correct' : '❌ RACE CONDITION DETECTED!'}`);
                    resolve();
                }
            });
        }
    });
}

// ============================================================================
// Version 3: Worker Threads WITH Atomics (FIXED)
// ============================================================================
function demonstrateWorkerThreadsFixed() {
    return new Promise((resolve) => {
        console.log("\n3. WORKER THREADS - FIXED (With Atomics)");
        console.log("--------------------------------------------------------------------------------");
        console.log("Atomics.add() provides lock-free synchronization");

        const sharedBuffer = new SharedArrayBuffer(4);
        const sharedArray = new Int32Array(sharedBuffer);
        sharedArray[0] = 0;

        let workersCompleted = 0;
        const totalWorkers = 10;

        for (let i = 0; i < totalWorkers; i++) {
            const worker = new Worker(__filename, {
                workerData: { sharedBuffer, iterations: 100, useAtomic: true }
            });

            worker.on('exit', () => {
                workersCompleted++;
                if (workersCompleted === totalWorkers) {
                    console.log(`Expected: 1000`);
                    console.log(`Actual:   ${sharedArray[0]}`);
                    console.log(`Status:   ✅ Correct! Atomics prevent race conditions`);
                    resolve();
                }
            });
        }
    });
}

// ============================================================================
// Version 4: Async/Await Pattern (NO RACE - single threaded)
// ============================================================================
class PageViewCounterAsync {
    constructor() {
        this.views = 0;
    }

    async increment() {
        // Even with delays, no race - event loop is sequential
        await new Promise(resolve => setTimeout(resolve, 1));
        this.views++;
    }

    getViews() {
        return this.views;
    }
}

async function demonstrateAsyncAwait() {
    console.log("\n4. ASYNC/AWAIT PATTERN (No Race - Sequential Event Loop)");
    console.log("--------------------------------------------------------------------------------");
    console.log("async/await doesn't create threads - still single-threaded!");

    const counter = new PageViewCounterAsync();

    // Even with async/await, operations are sequential
    const promises = [];
    for (let i = 0; i < 100; i++) {
        promises.push(counter.increment());
    }

    await Promise.all(promises);

    console.log(`Expected: 100`);
    console.log(`Actual:   ${counter.getViews()}`);
    console.log(`Status:   ✅ Correct! async/await is still single-threaded`);
}

// ============================================================================
// Worker Thread Code
// ============================================================================
if (!isMainThread) {
    const { sharedBuffer, iterations, useAtomic } = workerData;
    const sharedArray = new Int32Array(sharedBuffer);

    for (let i = 0; i < iterations; i++) {
        if (useAtomic) {
            // CORRECT: Atomic increment (thread-safe)
            Atomics.add(sharedArray, 0, 1);
        } else {
            // WRONG: Non-atomic increment (race condition)
            const temp = sharedArray[0];
            sharedArray[0] = temp + 1;
        }
    }

    process.exit(0);
}

// ============================================================================
// Main Execution
// ============================================================================
async function main() {
    if (isMainThread) {
        // Run all demonstrations
        await demonstrateSingleThreaded();
        await demonstrateWorkerThreadsBroken();
        await demonstrateWorkerThreadsFixed();
        await demonstrateAsyncAwait();
        printSummary();
    }
}

function printSummary() {
    console.log("\n================================================================================");
    console.log("                          SUMMARY");
    console.log("================================================================================");
    console.log(`
🎯 Key Lessons:

1. JavaScript is SINGLE-THREADED by default
   - Event loop processes one task at a time
   - No race conditions in normal async code
   - async/await is NOT multi-threading

2. Worker Threads CAN have races
   - SharedArrayBuffer allows shared memory
   - Multiple workers = true parallelism
   - Need synchronization like other languages

3. Synchronization in JavaScript:
   a) Atomics API
      - Atomics.add(), Atomics.sub(), etc.
      - Lock-free operations
      - Only works with SharedArrayBuffer

   b) Message passing (recommended)
      - postMessage() / onmessage
      - No shared memory = no races
      - The "JavaScript way"

4. When do you need synchronization?
   - Worker threads with SharedArrayBuffer? YES
   - Regular async/await? NO
   - Promises? NO
   - setTimeout/setInterval? NO

5. Best practices:
   - Default: Use async/await (no locks needed)
   - Worker threads: Prefer message passing over shared memory
   - If shared memory: Use Atomics
   - Don't create worker threads unless truly needed

6. Why JavaScript is different:
   - Python/Java/Go: Multi-threaded by default
   - JavaScript: Single-threaded with opt-in parallelism
   - Most JS code never needs locks
   - But when using workers, same rules apply!

⚠️  Don't assume "JavaScript is safe from races" - Worker threads +
    SharedArrayBuffer have the SAME race conditions as other languages!

💡 Run this example:
    node page_view_counter.js
`);
}

// Run the main function
main().catch(console.error);
