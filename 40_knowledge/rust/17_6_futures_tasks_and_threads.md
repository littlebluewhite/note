---
title: 17.6 Futures, Tasks, and Threads
note_type: knowledge
domain: rust
tags: [rust_book, knowledge, rust]
created: 2026-02-03
updated: 2026-02-03
status: active
source: note
---
# 17.6 Futures, Tasks, and Threads

## [Putting It All Together: Futures, Tasks, and Threads](https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html#putting-it-all-together-futures-tasks-and-threads)

## 融會貫通：Futures、Tasks 與 Threads

As we saw in [Chapter 16](http://localhost:3000/ch16-00-concurrency.html), threads provide one approach to concurrency. We’ve seen another approach in this chapter: using async with futures and streams. If you’re wondering when to choose one method over the other, the answer is: it depends! And in many cases, the choice isn’t threads _or_ async but rather threads _and_ async.

如同我們在第 16 章看到的，執行緒提供了一種並發的方法。本章也看到另一種方法：搭配 future 與串流使用非同步。如果你在想什麼時候該選哪一種，答案是：視情況而定！而且在很多情況下，選擇不是執行緒 _或_ 非同步，而是執行緒 _與_ 非同步。

Many operating systems have supplied threading-based concurrency models for decades now, and many programming languages support them as a result. However, these models are not without their tradeoffs. On many operating systems, they use a fair bit of memory for each thread. Threads are also only an option when your operating system and hardware support them. Unlike mainstream desktop and mobile computers, some embedded systems don’t have an OS at all, so they also don’t have threads.

許多作業系統數十年來一直提供以執行緒為基礎的並發模型，因此許多程式語言也支援它們。然而，這些模型並非沒有取捨。在許多作業系統上，每個執行緒都會占用相當多的記憶體。執行緒也只有在你的作業系統與硬體支援時才是選項。不像主流的桌上型與行動裝置，有些嵌入式系統根本沒有作業系統，因此也沒有執行緒。

The async model provides a different—and ultimately complementary—set of tradeoffs. In the async model, concurrent operations don’t require their own threads. Instead, they can run on tasks, as when we used `trpl::spawn_task` to kick off work from a synchronous function in the streams section. A task is similar to a thread, but instead of being managed by the operating system, it’s managed by library-level code: the runtime.

非同步模型提供了一組不同——而且最終互補——的取捨。在非同步模型中，並發操作不需要各自的執行緒。相反地，它們可以在任務上執行，就像我們在串流一節中使用 `trpl::spawn_task` 從同步函式啟動工作一樣。任務類似於執行緒，但它不是由作業系統管理，而是由函式庫層級的程式碼管理：執行時。

There’s a reason the APIs for spawning threads and spawning tasks are so similar. Threads act as a boundary for sets of synchronous operations; concurrency is possible _between_ threads. Tasks act as a boundary for sets of _asynchronous_ operations; concurrency is possible both _between_ and _within_ tasks, because a task can switch between futures in its body. Finally, futures are Rust’s most granular unit of concurrency, and each future may represent a tree of other futures. The runtime—specifically, its executor—manages tasks, and tasks manage futures. In that regard, tasks are similar to lightweight, runtime-managed threads with added capabilities that come from being managed by a runtime instead of by the operating system.

產生執行緒與產生任務的 API 之所以如此相似是有原因的。執行緒是同步操作集合的邊界；並發發生在執行緒之間。任務則是非同步操作集合的邊界；並發既可以發生在任務之間，也可以發生在任務之內，因為一個任務可以在其本體中切換不同的 futures。最後，future 是 Rust 最細粒度的並發單位，而每個 future 可能代表一棵由其他 futures 組成的樹。執行時——尤其是它的執行器——負責管理任務，而任務再管理 futures。從這個角度看，任務就像是由執行時管理的輕量執行緒，並因為由執行時而非作業系統管理而具備額外能力。

This doesn’t mean that async tasks are always better than threads (or vice versa). Concurrency with threads is in some ways a simpler programming model than concurrency with `async`. That can be a strength or a weakness. Threads are somewhat “fire and forget”; they have no native equivalent to a future, so they simply run to completion without being interrupted except by the operating system itself.

這並不表示非同步任務總是比執行緒更好（或反過來）。用執行緒進行並發在某些方面比用 `async` 更簡單。這可能是優點也可能是缺點。執行緒有點像「發射後不管（fire and forget）」；它們沒有與 future 對應的原生概念，因此只會一路跑到結束，除非作業系統本身打斷它們。

And it turns out that threads and tasks often work very well together, because tasks can (at least in some runtimes) be moved around between threads. In fact, under the hood, the runtime we’ve been using—including the `spawn_blocking` and `spawn_task` functions—is multithreaded by default! Many runtimes use an approach called _work stealing_ to transparently move tasks around between threads, based on how the threads are currently being utilized, to improve the system’s overall performance. That approach actually requires threads _and_ tasks, and therefore futures.

而事實上，執行緒與任務往往能非常好地協同運作，因為任務（至少在某些執行時中）可以在執行緒之間移動。實際上，在底層，我們一直使用的執行時——包含 `spawn_blocking` 與 `spawn_task` 函式——預設就是多執行緒！許多執行時使用一種稱為「工作竊取（work stealing）」的方法，依照執行緒目前的利用情況，在執行緒之間透明地移動任務，以提升系統整體效能。這種方法其實需要執行緒 _與_ 任務，因此也需要 futures。

When thinking about which method to use when, consider these rules of thumb:

在思考什麼時候該用哪種方法時，可以考慮以下經驗法則：

- If the work is _very parallelizable_ (that is, CPU-bound), such as processing a bunch of data where each part can be processed separately, threads are a better choice.

- If the work is _very concurrent_ (that is, I/O-bound), such as handling messages from a bunch of different sources that may come in at different intervals or different rates, async is a better choice.

- 如果工作是非常可平行化的（也就是 CPU 密集型），例如處理一大堆資料且每一部分都能分開處理，執行緒是更好的選擇。

- 如果工作是非常並發的（也就是 I/O 密集型），例如處理來自許多不同來源、可能以不同間隔或不同速率進來的訊息，非同步是更好的選擇。

And if you need both parallelism and concurrency, you don’t have to choose between threads and async. You can use them together freely, letting each play the part it’s best at. For example, Listing 17-25 shows a fairly common example of this kind of mix in real-world Rust code.

而如果你同時需要平行性與並發性，你不必在執行緒和非同步之間做選擇。你可以自由地一起使用它們，讓各自發揮最擅長的角色。例如，清單 17-25 展示了實際 Rust 程式碼中相當常見的混合用法。

Filename: src/main.rs

檔案名稱：src/main.rs
```rust
extern crate trpl; // for mdbook test

use std::{thread, time::Duration};

fn main() {
    let (tx, mut rx) = trpl::channel();

    thread::spawn(move || {
        for i in 1..11 {
            tx.send(i).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    trpl::block_on(async {
        while let Some(message) = rx.recv().await {
            println!("{message}");
        }
    });
}
```

[Listing 17-25](https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html#listing-17-25): Sending messages with blocking code in a thread and awaiting the messages in an async block

清單 17-25：在執行緒中用阻塞程式碼送出訊息，並在非同步區塊中等待訊息

We begin by creating an async channel, then spawning a thread that takes ownership of the sender side of the channel using the `move` keyword. Within the thread, we send the numbers 1 through 10, sleeping for a second between each. Finally, we run a future created with an async block passed to `trpl::block_on` just as we have throughout the chapter. In that future, we await those messages, just as in the other message-passing examples we have seen.

我們先建立一個非同步通道，接著產生一個執行緒，使用 `move` 關鍵字取得通道送端的所有權。在該執行緒中，我們送出 1 到 10 的數字，每次之間都睡一秒。最後，我們像本章其他地方一樣，執行一個由非同步區塊建立並傳給 `trpl::block_on` 的 future。在該 future 中，我們等待那些訊息，就如同其他訊息傳遞的例子一樣。

To return to the scenario we opened the chapter with, imagine running a set of video encoding tasks using a dedicated thread (because video encoding is compute-bound) but notifying the UI that those operations are done with an async channel. There are countless examples of these kinds of combinations in real-world use cases.

回到本章開頭的情境，想像用專用執行緒來執行一組影片編碼任務（因為影片編碼是計算密集），但用非同步通道通知 UI 這些操作已完成。這類組合在真實世界的使用案例中數不勝數。

## [Summary](https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html#summary)

## 總結

This isn’t the last you’ll see of concurrency in this book. The project in [Chapter 21](https://doc.rust-lang.org/book/ch21-00-final-project-a-web-server.html) will apply these concepts in a more realistic situation than the simpler examples discussed here and compare problem-solving with threading versus tasks and futures more directly.

這不會是你在本書中最後一次看到並發。第 21 章的專案會在比這裡討論的簡化示例更真實的情境中應用這些概念，並更直接地比較以執行緒對上任務與 futures 的問題解決方式。

No matter which of these approaches you choose, Rust gives you the tools you need to write safe, fast, concurrent code—whether for a high-throughput web server or an embedded operating system.

不論你選擇哪種方法，Rust 都提供你所需的工具來撰寫安全、快速的並發程式碼——無論是高吞吐量的網頁伺服器，還是嵌入式作業系統。

Next, we’ll talk about idiomatic ways to model problems and structure solutions as your Rust programs get bigger. In addition, we’ll discuss how Rust’s idioms relate to those you might be familiar with from object-oriented programming.

接下來，我們會談談當你的 Rust 程式變得更大時，如何用慣用的方式建模問題並組織解法。此外，我們也會討論 Rust 的慣用寫法與你可能從物件導向程式設計中熟悉的方式有何關聯。
