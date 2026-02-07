---
title: 17.4 Streams Futures in Sequence
note_type: knowledge
domain: rust
tags: [rust_book, knowledge, rust]
created: 2026-02-03
updated: 2026-02-03
status: active
source: note
canonical: rust_book/17.4 Streams Futures in Sequence.md
---
# 17.4 Streams Futures in Sequence

## [Streams: Futures in Sequence](https://doc.rust-lang.org/book/ch17-04-streams.html#streams-futures-in-sequence)
## 串流:序列中的 Future

So far in this chapter, we've mostly stuck to individual futures. The one big exception was the async channel we used. Recall how we used the receiver for our async channel earlier in this chapter in the ["Message Passing"](https://doc.rust-lang.org/book/ch17-02-concurrency-with-async.html#message-passing) section. The async `recv` method produces a sequence of items over time. This is an instance of a much more general pattern known as a _stream_.

到目前為止,在本章中我們大多堅持使用個別的 future。唯一的重大例外是我們使用的非同步通道。回想一下我們在本章前面「訊息傳遞」一節中如何使用非同步通道的接收器。非同步的 `recv` 方法會隨著時間產生一系列的項目。這是一個更通用模式的實例,稱為_串流_ (stream)。

We saw a sequence of items back in Chapter 13, when we looked at the `Iterator` trait in [The Iterator Trait and the `next` Method](https://doc.rust-lang.org/book/ch13-02-iterators.html#the-iterator-trait-and-the-next-method) section, but there are two differences between iterators and the async channel receiver. The first difference is time: iterators are synchronous, while the channel receiver is asynchronous. The second is the API. When working directly with `Iterator`, we call its synchronous `next` method. With the `trpl::Receiver` stream in particular, we called an asynchronous `recv` method instead. Otherwise, these APIs feel very similar, and that similarity isn't a coincidence. A stream is like an asynchronous form of iteration. Whereas the `trpl::Receiver` specifically waits to receive messages, though, the general-purpose stream API is much broader: it provides the next item the way `Iterator` does, but asynchronously.

我們在第 13 章看到過項目序列,當時我們在「Iterator trait 與 `next` 方法」一節中研究了 `Iterator` trait,但迭代器與非同步通道接收器之間有兩個差異。第一個差異是時間:迭代器是同步的,而通道接收器是非同步的。第二個是 API。當直接使用 `Iterator` 時,我們呼叫它的同步 `next` 方法。而對於 `trpl::Receiver` 串流,我們改為呼叫非同步的 `recv` 方法。除此之外,這些 API 感覺非常相似,這種相似性並非巧合。串流就像是非同步形式的迭代。然而,`trpl::Receiver` 特別等待接收訊息,而通用的串流 API 則更廣泛:它以 `Iterator` 的方式提供下一個項目,但是以非同步方式。

The similarity between iterators and streams in Rust means we can actually create a stream from any iterator. As with an iterator, we can work with a stream by calling its `next` method and then awaiting the output, as in Listing 17-30.

Rust 中迭代器與串流之間的相似性意味著我們實際上可以從任何迭代器創建串流。與迭代器一樣,我們可以透過呼叫其 `next` 方法然後等待輸出來使用串流,如清單 17-30 所示。

Filename: src/main.rs

[![50](https://doc.rust-lang.org/book/img/ferris/does_not_compile.svg "This code does not compile!")](https://doc.rust-lang.org/book/ch00-00-introduction.html#ferris)
```rust
extern crate trpl; // required for mdbook test

fn main() {
    trpl::run(async {
        let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        let iter = values.iter().map(|n| n * 2);
        let mut stream = trpl::stream_from_iter(iter);

        while let Some(value) = stream.next().await {
            println!("The value was: {value}");
        }
    });
}
```
[Listing 17-30](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-30): Creating a stream from an iterator and printing its values

清單 17-30: 從迭代器創建串流並列印其值

We start with an array of numbers, which we convert to an iterator and then call `map` on to double all the values. Then we convert the iterator into a stream using the `trpl::stream_from_iter` function. Next, we loop over the items in the stream as they arrive with the `while let` loop.

我們從一個數字陣列開始,將其轉換為迭代器,然後呼叫 `map` 將所有值加倍。接著我們使用 `trpl::stream_from_iter` 函式將迭代器轉換為串流。然後,我們使用 `while let` 迴圈在項目到達時遍歷串流中的項目。

Unfortunately, when we try to run the code, it doesn't compile, but instead it reports that there's no `next` method available:

不幸的是,當我們嘗試執行程式碼時,它無法編譯,而是報告沒有可用的 `next` 方法:

```
error[E0599]: no method named `next` found for struct `Iter` in the current scope
  --> src/main.rs:10:40
   |
10 |         while let Some(value) = stream.next().await {
   |                                        ^^^^
   |
   = note: the full type name has been written to 'file:///projects/async-await/target/debug/deps/async_await-575db3dd3197d257.long-type-14490787947592691573.txt'
   = note: consider using `--verbose` to print the full type name to the console
   = help: items from traits can only be used if the trait is in scope
help: the following traits which provide `next` are implemented but not in scope; perhaps you want to import one of them
   |
1  + use crate::trpl::StreamExt;
   |
1  + use futures_util::stream::stream::StreamExt;
   |
1  + use std::iter::Iterator;
   |
1  + use std::str::pattern::Searcher;
   |
help: there is a method `try_next` with a similar name
   |
10 |         while let Some(value) = stream.try_next().await {
   |                                        ~~~~~~~~
```

As this output explains, the reason for the compiler error is that we need the right trait in scope to be able to use the `next` method. Given our discussion so far, you might reasonably expect that trait to be `Stream`, but it's actually `StreamExt`. Short for _extension_, `Ext` is a common pattern in the Rust community for extending one trait with another.

正如此輸出所解釋的,編譯器錯誤的原因是我們需要在作用域中有正確的 trait 才能使用 `next` 方法。根據我們到目前為止的討論,您可能合理地預期該 trait 是 `Stream`,但實際上是 `StreamExt`。`Ext` 是_擴充_ (extension) 的縮寫,是 Rust 社群中用一個 trait 擴充另一個 trait 的常見模式。

We'll explain the `Stream` and `StreamExt` traits in a bit more detail at the end of the chapter, but for now all you need to know is that the `Stream` trait defines a low-level interface that effectively combines the `Iterator` and `Future` traits. `StreamExt` supplies a higher-level set of APIs on top of `Stream`, including the `next` method as well as other utility methods similar to those provided by the `Iterator` trait. `Stream` and `StreamExt` are not yet part of Rust's standard library, but most ecosystem crates use the same definition.

我們將在本章結尾更詳細地解釋 `Stream` 和 `StreamExt` trait,但現在您只需要知道 `Stream` trait 定義了一個低階介面,有效地結合了 `Iterator` 和 `Future` trait。`StreamExt` 在 `Stream` 之上提供了一組更高階的 API,包括 `next` 方法以及類似於 `Iterator` trait 提供的其他實用方法。`Stream` 和 `StreamExt` 尚未成為 Rust 標準函式庫的一部分,但大多數生態系統 crate 使用相同的定義。

The fix to the compiler error is to add a `use` statement for `trpl::StreamExt`, as in Listing 17-31.

修正編譯器錯誤的方法是為 `trpl::StreamExt` 新增一個 `use` 陳述式,如清單 17-31 所示。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use trpl::StreamExt;

fn main() {
    trpl::run(async {
        let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        let iter = values.iter().map(|n| n * 2);
        let mut stream = trpl::stream_from_iter(iter);

        while let Some(value) = stream.next().await {
            println!("The value was: {value}");
        }
    });
}
```
[Listing 17-31](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-31): Successfully using an iterator as the basis for a stream

清單 17-31: 成功使用迭代器作為串流的基礎

With all those pieces put together, this code works the way we want! What's more, now that we have `StreamExt` in scope, we can use all of its utility methods, just as with iterators. For example, in Listing 17-32, we use the `filter` method to filter out everything but multiples of three and five.

將所有這些部分組合在一起後,這段程式碼就能按我們想要的方式運作了!更重要的是,現在我們在作用域中有了 `StreamExt`,我們可以使用它的所有實用方法,就像使用迭代器一樣。例如,在清單 17-32 中,我們使用 `filter` 方法過濾掉除了三和五的倍數之外的所有內容。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use trpl::StreamExt;

fn main() {
    trpl::run(async {
        let values = 1..101;
        let iter = values.map(|n| n * 2);
        let stream = trpl::stream_from_iter(iter);

        let mut filtered =
            stream.filter(|value| value % 3 == 0 || value % 5 == 0);

        while let Some(value) = filtered.next().await {
            println!("The value was: {value}");
        }
    });
}
```
[Listing 17-32](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-32): Filtering a stream with the `StreamExt::filter` method

清單 17-32: 使用 `StreamExt::filter` 方法過濾串流

Of course, this isn't very interesting, since we could do the same with normal iterators and without any async at all. Let's look at what we can do that _is_ unique to streams.

當然,這並不是很有趣,因為我們可以使用普通的迭代器做同樣的事情,而且完全不需要 async。讓我們看看串流_獨有_的功能。

### [Composing Streams](https://doc.rust-lang.org/book/ch17-04-streams.html#composing-streams)
### 組合串流

Many concepts are naturally represented as streams: items becoming available in a queue, chunks of data being pulled incrementally from the filesystem when the full data set is too large for the computer's memory, or data arriving over the network over time. Because streams are futures, we can use them with any other kind of future and combine them in interesting ways. For example, we can batch up events to avoid triggering too many network calls, set timeouts on sequences of long-running operations, or throttle user interface events to avoid doing needless work.

許多概念自然地表示為串流:在佇列中變得可用的項目、當完整資料集對電腦記憶體來說太大時從檔案系統逐步提取的資料塊,或隨著時間透過網路到達的資料。因為串流是 future,我們可以將它們與任何其他類型的 future 一起使用,並以有趣的方式組合它們。例如,我們可以批次處理事件以避免觸發太多網路呼叫、為長時間執行的操作序列設定逾時,或限制使用者介面事件以避免做不必要的工作。

Let's start by building a little stream of messages as a stand-in for a stream of data we might see from a WebSocket or another real-time communication protocol, as shown in Listing 17-33.

讓我們從建立一個小的訊息串流開始,作為我們可能從 WebSocket 或其他即時通訊協定看到的資料串流的替代品,如清單 17-33 所示。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let mut messages = get_messages();

        while let Some(message) = messages.next().await {
            println!("{message}");
        }
    });
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
    for message in messages {
        tx.send(format!("Message: '{message}'")).unwrap();
    }

    ReceiverStream::new(rx)
}
```
[Listing 17-33](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-33): Using the `rx` receiver as a `ReceiverStream`

清單 17-33: 將 `rx` 接收器用作 `ReceiverStream`

First, we create a function called `get_messages` that returns `impl Stream<Item = String>`. For its implementation, we create an async channel, loop over the first 10 letters of the English alphabet, and send them across the channel.

首先,我們建立一個名為 `get_messages` 的函式,它回傳 `impl Stream<Item = String>`。在其實作中,我們建立一個非同步通道,遍歷英文字母表的前 10 個字母,並透過通道發送它們。

We also use a new type: `ReceiverStream`, which converts the `rx` receiver from the `trpl::channel` into a `Stream` with a `next` method. Back in `main`, we use a `while let` loop to print all the messages from the stream.

我們還使用了一個新類型:`ReceiverStream`,它將來自 `trpl::channel` 的 `rx` 接收器轉換為具有 `next` 方法的 `Stream`。回到 `main` 中,我們使用 `while let` 迴圈列印串流中的所有訊息。

When we run this code, we get exactly the results we would expect:

當我們執行這段程式碼時,我們得到了我們預期的結果:

```
Message: 'a'
Message: 'b'
Message: 'c'
Message: 'd'
Message: 'e'
Message: 'f'
Message: 'g'
Message: 'h'
Message: 'i'
Message: 'j'
```

Again, we could do this with the regular `Receiver` API or even the regular `Iterator` API, though, so let's add a feature that requires streams: adding a timeout that applies to every item in the stream, and a delay on the items we emit, as shown in Listing 17-34.

同樣,我們可以使用常規的 `Receiver` API 甚至常規的 `Iterator` API 做到這一點,所以讓我們新增一個需要串流的功能:為串流中的每個項目新增逾時,並為我們發出的項目新增延遲,如清單 17-34 所示。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};
use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let mut messages =
            pin!(get_messages().timeout(Duration::from_millis(200)));

        while let Some(result) = messages.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
    for message in messages {
        tx.send(format!("Message: '{message}'")).unwrap();
    }

    ReceiverStream::new(rx)
}
```
[Listing 17-34](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-34): Using the `StreamExt::timeout` method to set a time limit on the items in a stream

清單 17-34: 使用 `StreamExt::timeout` 方法為串流中的項目設定時間限制

We start by adding a timeout to the stream with the `timeout` method, which comes from the `StreamExt` trait. Then we update the body of the `while let` loop, because the stream now returns a `Result`. The `Ok` variant indicates a message arrived in time; the `Err` variant indicates that the timeout elapsed before any message arrived. We `match` on that result and either print the message when we receive it successfully or print a notice about the timeout. Finally, notice that we pin the messages after applying the timeout to them, because the timeout helper produces a stream that needs to be pinned to be polled.

我們首先使用來自 `StreamExt` trait 的 `timeout` 方法為串流新增逾時。然後我們更新 `while let` 迴圈的主體,因為串流現在回傳一個 `Result`。`Ok` 變體表示訊息及時到達;`Err` 變體表示在任何訊息到達之前逾時已過。我們對該結果進行 `match`,並在成功接收訊息時列印訊息,或列印有關逾時的通知。最後,請注意我們在對訊息應用逾時後將其固定,因為逾時輔助工具會產生一個需要固定才能輪詢的串流。

However, because there are no delays between messages, this timeout does not change the behavior of the program. Let's add a variable delay to the messages we send, as shown in Listing 17-35.

然而,由於訊息之間沒有延遲,此逾時不會改變程式的行為。讓我們為發送的訊息新增可變延遲,如清單 17-35 所示。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let mut messages =
            pin!(get_messages().timeout(Duration::from_millis(200)));

        while let Some(result) = messages.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            tx.send(format!("Message: '{message}'")).unwrap();
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-35](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-35): Sending messages through `tx` with an async delay without making `get_messages` an async function

清單 17-35: 在不使 `get_messages` 成為非同步函式的情況下,透過 `tx` 以非同步延遲發送訊息

In `get_messages`, we use the `enumerate` iterator method with the `messages` array so that we can get the index of each item we're sending along with the item itself. Then we apply a 100-millisecond delay to even-index items and a 300-millisecond delay to odd-index items to simulate the different delays we might see from a stream of messages in the real world. Because our timeout is for 200 milliseconds, this should affect half of the messages.

在 `get_messages` 中,我們對 `messages` 陣列使用 `enumerate` 迭代器方法,以便我們可以獲得正在發送的每個項目的索引以及項目本身。然後我們對偶數索引項目應用 100 毫秒延遲,對奇數索引項目應用 300 毫秒延遲,以模擬我們在現實世界中可能從訊息串流中看到的不同延遲。因為我們的逾時為 200 毫秒,這應該會影響一半的訊息。

To sleep between messages in the `get_messages` function without blocking, we need to use async. However, we can't make `get_messages` itself into an async function, because then we'd return a `Future<Output = Stream<Item = String>>` instead of a `Stream<Item = String>>`. The caller would have to await `get_messages` itself to get access to the stream. But remember: everything in a given future happens linearly; concurrency happens _between_ futures. Awaiting `get_messages` would require it to send all the messages, including the sleep delay between each message, before returning the receiver stream. As a result, the timeout would be useless. There would be no delays in the stream itself; they would all happen before the stream was even available.

要在 `get_messages` 函式中在訊息之間休眠而不阻塞,我們需要使用 async。然而,我們不能將 `get_messages` 本身變成非同步函式,因為那樣我們會回傳 `Future<Output = Stream<Item = String>>` 而不是 `Stream<Item = String>>`。呼叫者必須等待 `get_messages` 本身才能存取串流。但請記住:在給定的 future 中,一切都是線性發生的;並發發生在 future _之間_。等待 `get_messages` 需要它發送所有訊息,包括每條訊息之間的休眠延遲,然後才回傳接收器串流。結果,逾時將變得無用。串流本身不會有延遲;它們都會在串流可用之前發生。

Instead, we leave `get_messages` as a regular function that returns a stream, and we spawn a task to handle the async `sleep` calls.

相反,我們將 `get_messages` 保留為回傳串流的常規函式,並產生一個任務來處理非同步 `sleep` 呼叫。

Note: Calling `spawn_task` in this way works because we already set up our runtime; had we not, it would cause a panic. Other implementations choose different tradeoffs: they might spawn a new runtime and avoid the panic but end up with a bit of extra overhead, or they may simply not provide a standalone way to spawn tasks without reference to a runtime. Make sure you know what tradeoff your runtime has chosen and write your code accordingly!

注意:以這種方式呼叫 `spawn_task` 有效,因為我們已經設定了我們的執行時;如果我們沒有,它會導致 panic。其他實作選擇了不同的權衡:它們可能會產生一個新的執行時並避免 panic,但最終會有一些額外的開銷,或者它們可能根本不提供在沒有引用執行時的情況下產生任務的獨立方式。請確保您知道您的執行時選擇了什麼權衡,並相應地編寫您的程式碼!

Now our code has a much more interesting result. Between every other pair of messages, a `Problem: Elapsed(())` error.

現在我們的程式碼有了更有趣的結果。在每隔一對訊息之間,會出現一個 `Problem: Elapsed(())` 錯誤。

```
Message: 'a'
Problem: Elapsed(())
Message: 'b'
Message: 'c'
Problem: Elapsed(())
Message: 'd'
Message: 'e'
Problem: Elapsed(())
Message: 'f'
Message: 'g'
Problem: Elapsed(())
Message: 'h'
Message: 'i'
Problem: Elapsed(())
Message: 'j'
```

The timeout doesn't prevent the messages from arriving in the end. We still get all of the original messages, because our channel is _unbounded_: it can hold as many messages as we can fit in memory. If the message doesn't arrive before the timeout, our stream handler will account for that, but when it polls the stream again, the message may now have arrived.

逾時不會阻止訊息最終到達。我們仍然收到所有原始訊息,因為我們的通道是_無界的_:它可以容納我們可以放入記憶體的盡可能多的訊息。如果訊息在逾時之前沒有到達,我們的串流處理程式將計入該情況,但當它再次輪詢串流時,訊息現在可能已經到達。

You can get different behavior if needed by using other kinds of channels or other kinds of streams more generally. Let's see one of those in practice by combining a stream of time intervals with this stream of messages.

如果需要,您可以透過使用其他類型的通道或更一般的其他類型的串流來獲得不同的行為。讓我們透過將時間間隔串流與此訊息串流結合,在實踐中看看其中之一。

### [Merging Streams](https://doc.rust-lang.org/book/ch17-04-streams.html#merging-streams)
### 合併串流

First, let's create another stream, which will emit an item every millisecond if we let it run directly. For simplicity, we can use the `sleep` function to send a message on a delay and combine it with the same approach we used in `get_messages` of creating a stream from a channel. The difference is that this time, we're going to send back the count of intervals that have elapsed, so the return type will be `impl Stream<Item = u32>`, and we can call the function `get_intervals` (see Listing 17-36).

首先,讓我們建立另一個串流,如果我們讓它直接執行,它將每毫秒發出一個項目。為了簡單起見,我們可以使用 `sleep` 函式在延遲後發送訊息,並將其與我們在 `get_messages` 中使用的從通道建立串流的相同方法結合。不同之處在於這次我們將發送已過去的間隔計數,因此回傳類型將是 `impl Stream<Item = u32>`,我們可以呼叫函式 `get_intervals`(參見清單 17-36)。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let mut messages =
            pin!(get_messages().timeout(Duration::from_millis(200)));

        while let Some(result) = messages.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            tx.send(format!("Message: '{message}'")).unwrap();
        }
    });

    ReceiverStream::new(rx)
}

fn get_intervals() -> impl Stream<Item = u32> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let mut count = 0;
        loop {
            trpl::sleep(Duration::from_millis(1)).await;
            count += 1;
            tx.send(count).unwrap();
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-36](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-36): Creating a stream with a counter that will be emitted once every millisecond

清單 17-36: 建立一個計數器串流,每毫秒發出一次

We start by defining a `count` in the task. (We could define it outside the task, too, but it's clearer to limit the scope of any given variable.) Then we create an infinite loop. Each iteration of the loop asynchronously sleeps for one millisecond, increments the count, and then sends it over the channel. Because this is all wrapped in the task created by `spawn_task`, all of it—including the infinite loop—will get cleaned up along with the runtime.

我們首先在任務中定義一個 `count`。(我們也可以在任務外部定義它,但限制任何給定變數的作用域更清楚。)然後我們建立一個無限迴圈。迴圈的每次迭代非同步休眠一毫秒,遞增計數,然後透過通道發送它。因為這一切都包裹在由 `spawn_task` 建立的任務中,所有這一切——包括無限迴圈——都將與執行時一起清理。

This kind of infinite loop, which ends only when the whole runtime gets torn down, is fairly common in async Rust: many programs need to keep running indefinitely. With async, this doesn't block anything else, as long as there is at least one await point in each iteration through the loop.

這種僅在整個執行時被拆除時才結束的無限迴圈,在非同步 Rust 中相當常見:許多程式需要無限期地繼續執行。使用 async,只要迴圈的每次迭代中至少有一個等待點,這不會阻塞其他任何東西。

Now, back in our main function's async block, we can attempt to merge the `messages` and `intervals` streams, as shown in Listing 17-37.

現在,回到我們 main 函式的非同步區塊中,我們可以嘗試合併 `messages` 和 `intervals` 串流,如清單 17-37 所示。

Filename: src/main.rs

[![50](https://doc.rust-lang.org/book/img/ferris/does_not_compile.svg "This code does not compile!")](https://doc.rust-lang.org/book/ch00-00-introduction.html#ferris)
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let messages = get_messages().timeout(Duration::from_millis(200));
        let intervals = get_intervals();
        let merged = messages.merge(intervals);

        while let Some(result) = merged.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            tx.send(format!("Message: '{message}'")).unwrap();
        }
    });

    ReceiverStream::new(rx)
}

fn get_intervals() -> impl Stream<Item = u32> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let mut count = 0;
        loop {
            trpl::sleep(Duration::from_millis(1)).await;
            count += 1;
            tx.send(count).unwrap();
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-37](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-37): Attempting to merge the `messages` and `intervals` streams

清單 17-37: 嘗試合併 `messages` 和 `intervals` 串流

We start by calling `get_intervals`. Then we merge the `messages` and `intervals` streams with the `merge` method, which combines multiple streams into one stream that produces items from any of the source streams as soon as the items are available, without imposing any particular ordering. Finally, we loop over that combined stream instead of over `messages`.

我們首先呼叫 `get_intervals`。然後我們使用 `merge` 方法合併 `messages` 和 `intervals` 串流,該方法將多個串流組合成一個串流,該串流一旦項目可用就從任何來源串流產生項目,而不強加任何特定順序。最後,我們遍歷該組合串流,而不是遍歷 `messages`。

At this point, neither `messages` nor `intervals` needs to be pinned or mutable, because both will be combined into the single `merged` stream. However, this call to `merge` doesn't compile! (Neither does the `next` call in the `while let` loop, but we'll come back to that.) This is because the two streams have different types. The `messages` stream has the type `Timeout<impl Stream<Item = String>>`, where `Timeout` is the type that implements `Stream` for a `timeout` call. The `intervals` stream has the type `impl Stream<Item = u32>`. To merge these two streams, we need to transform one of them to match the other. We'll rework the intervals stream, because messages is already in the basic format we want and has to handle timeout errors (see Listing 17-38).

此時,`messages` 和 `intervals` 都不需要被固定或可變,因為兩者都將組合成單個 `merged` 串流。然而,這個對 `merge` 的呼叫無法編譯!(在 `while let` 迴圈中的 `next` 呼叫也無法編譯,但我們稍後會回到這個問題。)這是因為這兩個串流具有不同的類型。`messages` 串流具有類型 `Timeout<impl Stream<Item = String>>`,其中 `Timeout` 是為 `timeout` 呼叫實作 `Stream` 的類型。`intervals` 串流具有類型 `impl Stream<Item = u32>`。要合併這兩個串流,我們需要將其中一個轉換為匹配另一個。我們將重新處理 intervals 串流,因為 messages 已經是我們想要的基本格式,並且必須處理逾時錯誤(參見清單 17-38)。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let messages = get_messages().timeout(Duration::from_millis(200));
        let intervals = get_intervals()
            .map(|count| format!("Interval: {count}"))
            .timeout(Duration::from_secs(10));
        let merged = messages.merge(intervals);
        let mut stream = pin!(merged);

        while let Some(result) = stream.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            tx.send(format!("Message: '{message}'")).unwrap();
        }
    });

    ReceiverStream::new(rx)
}

fn get_intervals() -> impl Stream<Item = u32> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let mut count = 0;
        loop {
            trpl::sleep(Duration::from_millis(1)).await;
            count += 1;
            tx.send(count).unwrap();
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-38](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-38): Aligning the type of the the `intervals` stream with the type of the `messages` stream

清單 17-38: 將 `intervals` 串流的類型與 `messages` 串流的類型對齊

First, we can use the `map` helper method to transform the `intervals` into a string. Second, we need to match the `Timeout` from `messages`. Because we don't actually _want_ a timeout for `intervals`, though, we can just create a timeout which is longer than the other durations we are using. Here, we create a 10-second timeout with `Duration::from_secs(10)`. Finally, we need to make `stream` mutable, so that the `while let` loop's `next` calls can iterate through the stream, and pin it so that it's safe to do so. That gets us _almost_ to where we need to be. Everything type checks. If you run this, though, there will be two problems. First, it will never stop! You'll need to stop it with ctrl-c. Second, the messages from the English alphabet will be buried in the midst of all the interval counter messages:

首先,我們可以使用 `map` 輔助方法將 `intervals` 轉換為字串。其次,我們需要匹配來自 `messages` 的 `Timeout`。然而,因為我們實際上_不想要_ `intervals` 的逾時,我們可以建立一個比我們使用的其他持續時間更長的逾時。在這裡,我們使用 `Duration::from_secs(10)` 建立一個 10 秒的逾時。最後,我們需要使 `stream` 可變,以便 `while let` 迴圈的 `next` 呼叫可以遍歷串流,並固定它以便安全地執行此操作。這讓我們_幾乎_達到我們需要的地方。所有類型檢查都通過了。但是,如果您執行此操作,將會有兩個問題。首先,它永遠不會停止!您需要使用 ctrl-c 停止它。其次,來自英文字母表的訊息將被埋沒在所有間隔計數器訊息中:

```
--snip--
Interval: 38
Interval: 39
Interval: 40
Message: 'a'
Interval: 41
Interval: 42
Interval: 43
--snip--
```

Listing 17-39 shows one way to solve these last two problems.

清單 17-39 顯示了解決最後兩個問題的一種方法。

Filename: src/main.rs
```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let messages = get_messages().timeout(Duration::from_millis(200));
        let intervals = get_intervals()
            .map(|count| format!("Interval: {count}"))
            .throttle(Duration::from_millis(100))
            .timeout(Duration::from_secs(10));
        let merged = messages.merge(intervals).take(20);
        let mut stream = pin!(merged);

        while let Some(result) = stream.next().await {
            match result {
                Ok(message) => println!("{message}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    })
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            tx.send(format!("Message: '{message}'")).unwrap();
        }
    });

    ReceiverStream::new(rx)
}

fn get_intervals() -> impl Stream<Item = u32> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let mut count = 0;
        loop {
            trpl::sleep(Duration::from_millis(1)).await;
            count += 1;
            tx.send(count).unwrap();
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-39](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-39): Using `throttle` and `take` to manage the merged streams

清單 17-39: 使用 `throttle` 和 `take` 來管理合併的串流

First, we use the `throttle` method on the `intervals` stream so that it doesn't overwhelm the `messages` stream. _Throttling_ is a way of limiting the rate at which a function will be called—or, in this case, how often the stream will be polled. Once every 100 milliseconds should do, because that's roughly how often our messages arrive.

首先,我們對 `intervals` 串流使用 `throttle` 方法,這樣它就不會壓倒 `messages` 串流。_限流_ (Throttling) 是一種限制函式被呼叫速率的方法——或者,在這種情況下,串流被輪詢的頻率。每 100 毫秒一次應該就可以了,因為這大約是我們訊息到達的頻率。

To limit the number of items we will accept from a stream, we apply the `take` method to the `merged` stream, because we want to limit the final output, not just one stream or the other.

要限制我們從串流中接受的項目數量,我們對 `merged` 串流應用 `take` 方法,因為我們想要限制最終輸出,而不僅僅是一個或另一個串流。

Now when we run the program, it stops after pulling 20 items from the stream, and the intervals don't overwhelm the messages. We also don't get `Interval: 100` or `Interval: 200` or so on, but instead get `Interval: 1`, `Interval: 2`, and so on—even though we have a source stream that _can_ produce an event every millisecond. That's because the `throttle` call produces a new stream that wraps the original stream so that the original stream gets polled only at the throttle rate, not its own "native" rate. We don't have a bunch of unhandled interval messages we're choosing to ignore. Instead, we never produce those interval messages in the first place! This is the inherent "laziness" of Rust's futures at work again, allowing us to choose our performance characteristics.

現在當我們執行程式時,它在從串流中提取 20 個項目後停止,並且間隔不會壓倒訊息。我們也不會得到 `Interval: 100` 或 `Interval: 200` 等等,而是得到 `Interval: 1`、`Interval: 2` 等等——即使我們有一個_可以_每毫秒產生一個事件的來源串流。這是因為 `throttle` 呼叫產生一個包裝原始串流的新串流,因此原始串流僅以限流速率輪詢,而不是其自己的「原生」速率。我們沒有一堆我們選擇忽略的未處理間隔訊息。相反,我們一開始就從未產生那些間隔訊息!這是 Rust future 固有的「惰性」再次發揮作用,讓我們選擇我們的效能特性。

```
Interval: 1
Message: 'a'
Interval: 2
Interval: 3
Problem: Elapsed(())
Interval: 4
Message: 'b'
Interval: 5
Message: 'c'
Interval: 6
Interval: 7
Problem: Elapsed(())
Interval: 8
Message: 'd'
Interval: 9
Message: 'e'
Interval: 10
Interval: 11
Problem: Elapsed(())
Interval: 12
```

There's one last thing we need to handle: errors! With both of these channel-based streams, the `send` calls could fail when the other side of the channel closes—and that's just a matter of how the runtime executes the futures that make up the stream. Up until now, we've ignored this possibility by calling `unwrap`, but in a well-behaved app, we should explicitly handle the error, at minimum by ending the loop so we don't try to send any more messages. Listing 17-40 shows a simple error strategy: print the issue and then `break` from the loops.

我們還需要處理最後一件事:錯誤!對於這兩個基於通道的串流,當通道的另一端關閉時,`send` 呼叫可能會失敗——這只是執行時如何執行組成串流的 future 的問題。到目前為止,我們透過呼叫 `unwrap` 忽略了這種可能性,但在一個表現良好的應用程式中,我們應該明確處理錯誤,至少透過結束迴圈,這樣我們就不會嘗試發送更多訊息。清單 17-40 顯示了一個簡單的錯誤策略:列印問題,然後從迴圈中 `break`。

```rust
extern crate trpl; // required for mdbook test

use std::{pin::pin, time::Duration};

use trpl::{ReceiverStream, Stream, StreamExt};

fn main() {
    trpl::run(async {
        let messages = get_messages().timeout(Duration::from_millis(200));
        let intervals = get_intervals()
            .map(|count| format!("Interval #{count}"))
            .throttle(Duration::from_millis(500))
            .timeout(Duration::from_secs(10));
        let merged = messages.merge(intervals).take(20);
        let mut stream = pin!(merged);

        while let Some(result) = stream.next().await {
            match result {
                Ok(item) => println!("{item}"),
                Err(reason) => eprintln!("Problem: {reason:?}"),
            }
        }
    });
}

fn get_messages() -> impl Stream<Item = String> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];

        for (index, message) in messages.into_iter().enumerate() {
            let time_to_sleep = if index % 2 == 0 { 100 } else { 300 };
            trpl::sleep(Duration::from_millis(time_to_sleep)).await;

            if let Err(send_error) = tx.send(format!("Message: '{message}'")) {
                eprintln!("Cannot send message '{message}': {send_error}");
                break;
            }
        }
    });

    ReceiverStream::new(rx)
}

fn get_intervals() -> impl Stream<Item = u32> {
    let (tx, rx) = trpl::channel();

    trpl::spawn_task(async move {
        let mut count = 0;
        loop {
            trpl::sleep(Duration::from_millis(1)).await;
            count += 1;

            if let Err(send_error) = tx.send(count) {
                eprintln!("Could not send interval {count}: {send_error}");
                break;
            };
        }
    });

    ReceiverStream::new(rx)
}
```
[Listing 17-40](https://doc.rust-lang.org/book/ch17-04-streams.html#listing-17-40): Handling errors and shutting down the loops

清單 17-40: 處理錯誤並關閉迴圈

As usual, the correct way to handle a message send error will vary; just make sure you have a strategy.

像往常一樣,處理訊息發送錯誤的正確方法會有所不同;只要確保您有一個策略。

Now that we've seen a bunch of async in practice, let's take a step back and dig into a few of the details of how `Future`, `Stream`, and the other key traits Rust uses to make async work.

現在我們已經在實踐中看到了很多 async,讓我們退一步,深入了解 `Future`、`Stream` 以及 Rust 用來使 async 工作的其他關鍵 trait 的一些細節。
