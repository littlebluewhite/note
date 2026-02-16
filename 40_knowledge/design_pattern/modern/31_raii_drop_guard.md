---
title: "RAII and Drop Guard / RAII 與 Drop 守衛模式"
note_type: knowledge
domain: design_pattern
category: modern
tags: [design-pattern, modern, go, rust, raii, drop-guard]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: design_pattern
chapter: "31"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# RAII and Drop Guard / RAII 與 Drop 守衛模式

## Intent / 意圖
> 將資源的生命週期綁定到物件的作用域，當物件離開作用域時自動釋放資源，確保即使在異常路徑下也不會發生資源洩漏。

## Problem / 問題情境
程式需要管理各種外部資源（檔案、網路連線、鎖、資料庫交易），這些資源必須在使用後正確釋放：

1. **資源洩漏**：開發者忘記呼叫 `Close()`、`Unlock()`、`Rollback()`，資源永遠不被釋放
2. **異常路徑遺漏**：在正常路徑有 cleanup，但 error return 或 panic 的路徑忘記釋放
3. **巢狀資源**：取得多個資源後，中途失敗需要按逆序釋放已取得的資源，手動管理容易出錯
4. **程式碼噪音**：每個函數都充斥 `defer close()` 或 try-finally，分散了業務邏輯的注意力

## Solution / 解決方案
RAII（Resource Acquisition Is Initialization）將資源的取得和釋放綁定到物件的建構和解構。在 Rust 中透過 `Drop` trait 實現：當值離開作用域時，編譯器自動插入 `drop()` 呼叫。在 Go 中沒有解構子，但可以用 `defer` 搭配守衛物件（guard）模擬部分行為。關鍵差異在於 Rust 的 ownership 系統提供編譯期保證，而 Go 的 `defer` 是一種紀律性的慣例。

## Structure / 結構

```mermaid
flowchart TB
    subgraph "Rust RAII"
        A1[建立物件 = 取得資源] --> A2[使用資源]
        A2 --> A3[離開作用域]
        A3 --> A4["自動呼叫 Drop::drop()"]
        A4 --> A5[資源釋放]
    end

    subgraph "Go defer"
        B1[取得資源] --> B2["defer resource.Close()"]
        B2 --> B3[使用資源]
        B3 --> B4[函數返回]
        B4 --> B5[執行 deferred 函數]
        B5 --> B6[資源釋放]
    end
```

## Participants / 參與者

| 角色 | 職責 |
|------|------|
| **Resource** | 需要管理的外部資源（file、lock、connection） |
| **Guard / Wrapper** | 持有資源的物件，在解構時負責釋放 |
| **Drop trait** | Rust 的解構 trait，定義資源釋放邏輯 |
| **defer** | Go 的延遲執行機制，在函數返回時執行清理 |
| **Scope** | 物件的生存範圍，離開 scope 觸發自動清理 |

## Go 實作

```go
package main

import (
	"fmt"
	"sync"
)

// --- 範例 1: Mutex Guard ---

type MutexGuard[T any] struct {
	mu    *sync.Mutex
	value *T
}

// Lock 取得鎖並回傳 guard，呼叫端必須 defer guard.Unlock()
func Lock[T any](mu *sync.Mutex, value *T) MutexGuard[T] {
	mu.Lock()
	fmt.Println("  [Guard] Lock acquired")
	return MutexGuard[T]{mu: mu, value: value}
}

func (g MutexGuard[T]) Get() *T {
	return g.value
}

func (g MutexGuard[T]) Unlock() {
	g.mu.Unlock()
	fmt.Println("  [Guard] Lock released")
}

// --- 範例 2: Transaction Guard ---

type TxState int

const (
	TxActive TxState = iota
	TxCommitted
	TxRolledBack
)

type Transaction struct {
	id    int
	state TxState
}

func BeginTx(id int) *Transaction {
	fmt.Printf("  [Tx %d] BEGIN\n", id)
	return &Transaction{id: id, state: TxActive}
}

func (tx *Transaction) Commit() {
	if tx.state == TxActive {
		tx.state = TxCommitted
		fmt.Printf("  [Tx %d] COMMIT\n", tx.id)
	}
}

// Guard 確保 Transaction 在函數結束時被 rollback（如果未 commit）
func (tx *Transaction) Guard() func() {
	return func() {
		if tx.state == TxActive {
			tx.state = TxRolledBack
			fmt.Printf("  [Tx %d] ROLLBACK (auto)\n", tx.id)
		}
	}
}

// --- 範例 3: File-like resource ---

type FileHandle struct {
	name   string
	closed bool
}

func OpenFile(name string) *FileHandle {
	fmt.Printf("  [File] Opened: %s\n", name)
	return &FileHandle{name: name}
}

func (f *FileHandle) Write(data string) {
	fmt.Printf("  [File] Write to %s: %s\n", f.name, data)
}

func (f *FileHandle) Close() {
	if !f.closed {
		f.closed = true
		fmt.Printf("  [File] Closed: %s\n", f.name)
	}
}

// --- 使用示範 ---

func successfulOperation() {
	fmt.Println("--- Successful Operation ---")

	tx := BeginTx(1)
	defer tx.Guard()() // defer 確保自動 rollback

	f := OpenFile("data.txt")
	defer f.Close() // defer 確保自動關閉

	f.Write("hello world")
	tx.Commit() // 明確 commit，Guard 中不會 rollback
}

func failedOperation() {
	fmt.Println("--- Failed Operation ---")

	tx := BeginTx(2)
	defer tx.Guard()() // defer 確保自動 rollback

	f := OpenFile("data.txt")
	defer f.Close()

	f.Write("partial data")
	// 模擬錯誤：沒有呼叫 tx.Commit()
	fmt.Println("  [Error] Something went wrong, returning early")
	// 函數返回時，defer 會自動 rollback 和關閉檔案
}

func mutexExample() {
	fmt.Println("--- Mutex Guard ---")

	var mu sync.Mutex
	counter := 0

	guard := Lock(&mu, &counter)
	defer guard.Unlock()

	*guard.Get() += 42
	fmt.Printf("  Counter: %d\n", *guard.Get())
}

func main() {
	successfulOperation()
	fmt.Println()
	failedOperation()
	fmt.Println()
	mutexExample()
}

// Output:
// --- Successful Operation ---
//   [Tx 1] BEGIN
//   [File] Opened: data.txt
//   [File] Write to data.txt: hello world
//   [Tx 1] COMMIT
//   [File] Closed: data.txt
//
// --- Failed Operation ---
//   [Tx 2] BEGIN
//   [File] Opened: data.txt
//   [File] Write to data.txt: partial data
//   [Error] Something went wrong, returning early
//   [File] Closed: data.txt
//   [Tx 2] ROLLBACK (auto)
//
// --- Mutex Guard ---
//   [Guard] Lock acquired
//   Counter: 42
//   [Guard] Lock released
```

## Rust 實作

```rust
use std::fmt;
use std::sync::Mutex;

// --- 範例 1: 自動釋放的 File Guard ---

struct FileHandle {
    name: String,
}

impl FileHandle {
    fn open(name: &str) -> Self {
        println!("  [File] Opened: {name}");
        FileHandle {
            name: name.to_string(),
        }
    }

    fn write(&self, data: &str) {
        println!("  [File] Write to {}: {data}", self.name);
    }
}

impl Drop for FileHandle {
    fn drop(&mut self) {
        println!("  [File] Closed: {} (auto Drop)", self.name);
    }
}

// --- 範例 2: Transaction Guard ---

#[derive(Debug, PartialEq)]
enum TxState {
    Active,
    Committed,
    RolledBack,
}

struct Transaction {
    id: u32,
    state: TxState,
}

impl Transaction {
    fn begin(id: u32) -> Self {
        println!("  [Tx {id}] BEGIN");
        Transaction {
            id,
            state: TxState::Active,
        }
    }

    fn commit(&mut self) {
        if self.state == TxState::Active {
            self.state = TxState::Committed;
            println!("  [Tx {}] COMMIT", self.id);
        }
    }
}

impl Drop for Transaction {
    fn drop(&mut self) {
        if self.state == TxState::Active {
            self.state = TxState::RolledBack;
            println!("  [Tx {}] ROLLBACK (auto Drop)", self.id);
        }
    }
}

// --- 範例 3: Mutex Guard (std::sync::MutexGuard 的簡化版) ---

struct Counter {
    value: Mutex<i32>,
}

impl Counter {
    fn new(initial: i32) -> Self {
        Counter {
            value: Mutex::new(initial),
        }
    }

    fn increment(&self, amount: i32) {
        // MutexGuard 在離開作用域時自動 unlock
        let mut guard = self.value.lock().unwrap();
        println!("  [Guard] Lock acquired");
        *guard += amount;
        println!("  Counter: {}", *guard);
        // guard 在這裡被 drop，自動 unlock
        println!("  [Guard] Lock will release at scope end");
    }
}

// --- 範例 4: Scope Guard (通用版) ---

struct ScopeGuard<F: FnOnce()> {
    callback: Option<F>,
}

impl<F: FnOnce()> ScopeGuard<F> {
    fn new(callback: F) -> Self {
        ScopeGuard {
            callback: Some(callback),
        }
    }

    /// 取消 guard，不會在 drop 時執行 callback
    fn dismiss(mut self) {
        self.callback.take();
    }
}

impl<F: FnOnce()> Drop for ScopeGuard<F> {
    fn drop(&mut self) {
        if let Some(callback) = self.callback.take() {
            callback();
        }
    }
}

// --- 使用示範 ---

fn successful_operation() {
    println!("--- Successful Operation ---");

    let mut tx = Transaction::begin(1);
    let file = FileHandle::open("data.txt");

    file.write("hello world");
    tx.commit();

    // tx 和 file 在函數結束時被 drop
    // tx 已 commit，Drop 中不會 rollback
    // file 自動 close
}

fn failed_operation() {
    println!("--- Failed Operation ---");

    let tx = Transaction::begin(2); // 注意：沒有 mut，不會 commit
    let file = FileHandle::open("data.txt");

    file.write("partial data");
    println!("  [Error] Something went wrong, returning early");

    // tx 未 commit，Drop 會自動 rollback
    // file 自動 close
}

fn scope_guard_example() {
    println!("--- Scope Guard ---");

    let resource = "temporary_resource";
    let _guard = ScopeGuard::new(|| {
        println!("  [ScopeGuard] Cleanup: releasing {resource}");
    });

    println!("  Using {resource}...");

    // guard 在函數結束時執行 cleanup
}

fn main() {
    successful_operation();
    println!();
    failed_operation();
    println!();

    let counter = Counter::new(0);
    println!("--- Mutex Guard ---");
    counter.increment(42);
    println!();

    scope_guard_example();
}

// Output:
// --- Successful Operation ---
//   [Tx 1] BEGIN
//   [File] Opened: data.txt
//   [File] Write to data.txt: hello world
//   [Tx 1] COMMIT
//   [File] Closed: data.txt (auto Drop)
//
// --- Failed Operation ---
//   [Tx 2] BEGIN
//   [File] Opened: data.txt
//   [File] Write to data.txt: partial data
//   [Error] Something went wrong, returning early
//   [File] Closed: data.txt (auto Drop)
//   [Tx 2] ROLLBACK (auto Drop)
//
// --- Mutex Guard ---
//   [Guard] Lock acquired
//   Counter: 42
//   [Guard] Lock will release at scope end
//
// --- Scope Guard ---
//   Using temporary_resource...
//   [ScopeGuard] Cleanup: releasing temporary_resource
```

## Go vs Rust 對照表

| 面向 | Go | Rust |
|------|----|----|
| 資源釋放機制 | `defer` 延遲呼叫 | `Drop` trait 自動呼叫 |
| 觸發時機 | 函數返回時 | 變數離開作用域時（更精確） |
| 編譯期保證 | 無（忘記 defer 不會報錯） | 有（所有值都保證被 drop） |
| 巢狀資源順序 | LIFO（最後 defer 最先執行） | LIFO（先宣告的後 drop） |
| 提前釋放 | 不支援（defer 綁定到函數結束） | `drop(value)` 手動提前釋放 |
| 取消釋放 | 需要用 flag 變數控制 | `std::mem::forget()` 或 `ManuallyDrop` |
| panic 行為 | defer 在 panic 時仍會執行 | Drop 在 panic unwind 時仍會執行 |

## When to Use / 適用場景

- 管理必須配對的 acquire/release 操作（open/close、lock/unlock、begin/commit-or-rollback）
- Rust 中任何持有外部資源的型別都應實作 `Drop`
- 需要確保即使在 error 或 panic 路徑下也能正確釋放資源
- 建構 scope guard 實現「不論發生什麼都要執行的清理邏輯」

## When NOT to Use / 不適用場景

- 資源的生命週期不是由作用域決定的（如放入集合中長期持有） -- 需要手動管理或使用 reference counting（`Arc`）
- 資源釋放有特定的順序要求且不符合 LIFO -- 需要手動控制順序
- 清理操作可能失敗且需要處理錯誤 -- `Drop` 不能回傳 `Result`，需要提供顯式的 `close()` 方法

## Real-World Examples / 真實世界案例

- **Rust `std::sync::MutexGuard`**：標準庫中最經典的 RAII 範例，`lock()` 回傳 `MutexGuard`，離開作用域自動 `unlock()`
- **Rust `std::fs::File`**：`File` 實作 `Drop` 自動關閉 file descriptor
- **Rust `scopeguard` crate**：提供通用的 scope guard 巨集 `defer!` 和 `guard!`
- **Go `database/sql.Tx`**：慣例搭配 `defer tx.Rollback()` 使用，commit 後 rollback 為 no-op

## Related Patterns / 相關模式

- **Proxy (GoF)**：Guard 物件作為資源的 proxy，控制存取並負責清理
- **Command (GoF)**：ScopeGuard 的 cleanup callback 本質上是一個 Command，延遲到 drop 時執行
- **Newtype (Modern)**：Guard 型別（如 `MutexGuard`）是 newtype 的應用，包裝底層資源並附加行為

## Pitfalls / 常見陷阱

1. **Go 的 defer 作用域是函數級別**：`defer` 在函數返回時才執行，不是在 block 結束時。在迴圈中 `defer` 會導致資源累積到函數結束才釋放，可能耗盡資源
2. **Rust 的 Drop 中不能 panic**：在 panic unwind 過程中的 double panic 會直接 abort。Drop 中的清理邏輯應該是 infallible 的
3. **忘記使用回傳值**：`let _ = mutex.lock()` 會立即 drop MutexGuard，鎖瞬間釋放。必須綁定到變數 `let guard = mutex.lock()`
4. **循環引用阻止 Drop**：`Rc<T>` 循環引用不會觸發 Drop，需要用 `Weak<T>` 打破循環。Go 的 GC 沒有這個問題

## References / 參考資料

- Rust Book - "Smart Pointers": https://doc.rust-lang.org/book/ch15-00-smart-pointers.html
- Rust Reference - Destructors: https://doc.rust-lang.org/reference/destructors.html
- Rust Design Patterns - RAII Guards: https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html
- Effective Go - Defer: https://go.dev/doc/effective_go#defer
- Stroustrup, "The C++ Programming Language" - RAII 的原始提出
