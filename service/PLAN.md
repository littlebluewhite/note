---
title: "電商平台規劃"
category: service
tags: [service]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: note
status: active
---
# 電商平台規劃

## 1) 目標與範圍

- 核心流程：瀏覽商品 -> 加入購物車 -> 結帳 -> 綠界付款 -> 訂單成立/失敗
- 角色：顧客、後台營運、系統管理員
- 前端：Svelte/SvelteKit，SSR + CSR 混合
- 後端：Rust/Axum + REST API

## 2) 模組拆分（後端）

- Identity/Access：登入、JWT、ABAC 授權
- Catalog：商品、分類、規格、圖片
- Pricing/Promotion：價格、折扣、優惠券
- Inventory：庫存管理、保留/釋放
- Cart：購物車與購物車項目
- Checkout：結帳流程、金流初始化
- Orders：訂單主檔/明細、狀態機
- Payment：綠界付款、回呼、對帳
- Shipping：出貨資料與物流整合（TBD）
- Notifications：Email/SMS（SendGrid）

## 3) 模組間溝通（單體）

- 同步需求：模組內直接函式呼叫（in-process），不引入 gRPC
- 非同步需求：domain events + outbox table + worker（可選 Redis）
- 交易一致性：以單一 DB transaction 為界，事件在同交易中寫入 outbox
- 對外通訊：REST API（SvelteKit/第三方）＋支付回呼

### 3.1) Outbox worker 流程（單體）

- 取件：`status = pending` 且 `next_run_at <= now()`，按 `created_at` 批次抓取
- 併發控制：`FOR UPDATE SKIP LOCKED`，避免多個 worker 重複處理
- 成功：標記 `sent`，記錄處理時間（可加欄位）
- 失敗：`attempts + 1`、寫入 `last_error`、用指數回退更新 `next_run_at`
- 死信：超過最大嘗試次數後標記 `dead`，人工處理或補償
- 冪等：以 `event_outbox.id` 作為事件唯一鍵，消費端做去重

## 4) 未來拆分策略（單體 -> 微服務）

- 先以清楚的模組邊界和介面設計，避免互相穿透
- 事件先落 outbox，未來可替換為 Kafka topics
- 拆分順序建議：Payment/Orders -> Catalog -> Inventory -> Notifications
- 拆分條件：團隊分工需求、流量/吞吐、獨立擴縮或可用性要求

## 5) ABAC 設計（高層）

- Subject attributes：user_id, roles, org_id, is_admin, is_active
- Resource attributes：owner_id, status, visibility, is_deleted
- Action：read, write, approve, refund, admin
- Context：ip, time, request_source
- 例：
  - 顧客可以讀取自己的訂單（resource.owner_id == subject.user_id）
  - 營運人員可更新商品（subject.roles 包含 "ops"）

## 6) 資料模型（初稿）

- users(id, email, password_hash, status, created_at)
- user_roles(user_id, role)
- abac_policies(id, subject, resource, action, condition)
- products(id, name, description, status, created_at)
- product_variants(id, product_id, sku, price, status)
- product_images(id, product_id, url, sort_order)
- categories(id, name, parent_id)
- product_categories(product_id, category_id)
- inventory(id, variant_id, qty_available, qty_reserved)
- carts(id, user_id, status, updated_at)
- cart_items(id, cart_id, variant_id, qty, price_snapshot)
- orders(id, user_id, status, total, currency, created_at)
- order_items(id, order_id, variant_id, qty, price_snapshot)
- order_addresses(id, order_id, type, name, phone, address1, address2, city, postal_code)
- payments(id, order_id, provider, status, amount, currency, txn_id, provider_ref)
- refunds(id, order_id, payment_id, status, amount, reason, provider_ref)
- shipments(id, order_id, status, carrier, tracking_no, shipped_at, delivered_at)
- coupons(id, code, type, value, start_at, end_at)
- order_coupons(order_id, coupon_id)
- event_outbox(id, aggregate_type, aggregate_id, event_type, payload, status, attempts, next_run_at, last_error, created_at)

## 7) 訂單/付款/退款狀態機（草案）

- Order status
  - pending_payment -> paid -> preparing_shipment -> shipped -> completed
  - pending_payment -> payment_failed -> cancelled
  - paid -> refund_requested -> refunded
  - paid -> refund_requested -> refund_rejected
- Payment status
  - created -> pending -> succeeded
  - created -> failed / cancelled
  - succeeded -> refunded (full/partial)
- Refund status
  - requested -> approved -> processing -> succeeded
  - requested -> rejected
  - processing -> failed
- 核心規則
  - 訂單建立時先保留庫存（reserved），付款成功後扣減（available/reserved 更新）
  - 付款失敗或逾時需釋放庫存
  - 已出貨訂單退款需先走退貨流程（TBD）

## 8) 物流/出貨流程（草案）

- 物流狀態
  - pending -> ready_to_ship -> shipped -> delivered
  - delivered -> returned (退貨)
  - pending/ready_to_ship -> cancelled
- 物流資料
  - checkout 時保留下單地址（order_addresses）
  - 後台建立出貨單，填 carrier + tracking_no
  - 出貨/送達時間由後台更新或物流回寫（TBD）

## 9) REST API（草案）

- Auth
  - POST /auth/login
  - POST /auth/logout
  - POST /auth/refresh
- Catalog
  - GET /products
  - GET /products/{id}
  - GET /categories
- Cart/Checkout
  - GET /cart
  - POST /cart/items
  - PATCH /cart/items/{id}
  - DELETE /cart/items/{id}
  - POST /checkout
- Orders/Payments
  - GET /orders
  - GET /orders/{id}
  - POST /orders/{id}/cancel
  - POST /orders/{id}/refunds
  - GET /orders/{id}/refunds
  - POST /payments/ecpay/notify (callback)
- Shipping
  - POST /admin/orders/{id}/shipments
  - PATCH /admin/shipments/{id}
- Admin
  - CRUD /admin/products
  - CRUD /admin/orders
  - CRUD /admin/coupons

## 10) Domain events（outbox，未來可對應 Kafka topic）

- order.created
- order.paid
- order.cancelled
- payment.succeeded
- payment.failed
- refund.requested
- refund.succeeded
- refund.failed
- shipment.created
- shipment.shipped
- shipment.delivered
- inventory.reserved
- inventory.released
- email.send

## 11) Redis 用途

- rate limiting
- short-lived cache（商品/類別列表）
- 可能的 session blacklist（JWT 失效清單）

## 12) S3 用途

- 商品圖與素材存放
- 透過後端產生預簽名 URL

## 13) 測試拆分

- backend：單元 + integration（API + DB）
- frontend：component + e2e（Playwright）

## 14) 前端技術細節（SvelteKit）

- 架構：`load` 分層（server/client），敏感資料走 server load
- 認證：JWT 以 httpOnly cookie 為主，401 觸發 refresh 流程
- 狀態：購物車/使用者用 Svelte stores，server load 初始化
- API client：統一 fetch wrapper（重試、401 refresh、trace id）
- SEO：商品/分類 SSR，結帳 CSR
- 路由：/products, /products/[id], /cart, /checkout, /orders, /admin
- 金流 UX：回跳結果頁 + 訂單狀態輪詢
- 圖片：S3 URL + CDN/縮圖策略
- 搜尋：query string 維持 filter/sort/page
- 表單：Zod + sveltekit-superforms（或自訂）
- 格式化：TWD 金額、時區顯示
- 測試：component + e2e（checkout/付款回跳）

### 14.1) IA 與 Wireflow（草案）

- 首頁 -> 商品列表 -> 商品詳情 -> 加入購物車 -> 購物車 -> 結帳 -> 綠界付款 -> 回跳結果 -> 訂單詳情
- 後台：登入 -> 商品管理 -> 訂單管理 -> 出貨/退款

### 14.2) 元件規劃（草案）

- Catalog：ProductCard, ProductGrid, CategoryNav, PriceBadge, RatingStars
- Product：ProductGallery, VariantSelector, AddToCartButton
- Cart/Checkout：CartItemRow, CartSummary, CheckoutForm, AddressForm, CouponInput
- Orders：OrderList, OrderDetail, OrderStatusBadge, RefundRequestForm
- Shared：AppHeader, AppFooter, Breadcrumbs, Pagination, EmptyState, LoadingSkeleton
- Admin：AdminLayout, ProductEditor, OrderTable, ShipmentForm

### 14.3) UI 狀態規範（草案）

- Loading：骨架 + 文字 placeholder
- Empty：清楚 CTA（回商品列表/清空條件）
- Error：顯示可恢復操作（重試/回上一頁）
- Optimistic：購物車更新/收藏
- 結帳：狀態鎖定（防重送）+ 倒數提示
- 付款回跳：結果頁 + 訂單狀態輪詢

### 14.4) 頁面路由與載入資料（草案）

- `/`：首頁（熱門商品、分類入口）
  - load：featured_products, categories
- `/products`：商品列表
  - load：products, filters, pagination
- `/products/[id]`：商品詳情
  - load：product, variants, images, stock_summary
- `/cart`：購物車
  - load：cart, cart_items, totals
- `/checkout`：結帳
  - load：cart, user_profile, shipping_methods
- `/orders`：訂單列表
  - load：orders, pagination
- `/orders/[id]`：訂單詳情
  - load：order, order_items, payments, shipments, refunds
- `/payment/result`：付款回跳結果
  - load：order_status, payment_status
- `/admin`：後台入口
  - load：user_roles, permissions
- `/admin/products`：商品管理
  - load：products, pagination
- `/admin/products/[id]`：商品編輯
  - load：product, variants, images
- `/admin/orders`：訂單管理
  - load：orders, filters, pagination
- `/admin/orders/[id]`：訂單詳情/出貨
  - load：order, shipments, refunds, payment

### 14.5) 元件 Props 介面（草案）

- ProductCard: { id, name, price, image_url, status }
- ProductGrid: { items, loading, onSelect }
- ProductGallery: { images, active_index }
- VariantSelector: { variants, selected_id, onChange }
- AddToCartButton: { variant_id, disabled, onAdd }
- CartItemRow: { item, onQtyChange, onRemove }
- CartSummary: { subtotal, discount, shipping, total }
- CheckoutForm: { address, onSubmit, submitting }
- AddressForm: { value, onChange, errors }
- CouponInput: { value, onApply, error }
- OrderList: { orders, loading, onSelect }
- OrderDetail: { order, items, payments, shipments, refunds }
- OrderStatusBadge: { status }
- RefundRequestForm: { max_amount, onSubmit, submitting }
- Pagination: { page, page_size, total, onChange }
- EmptyState: { title, description, action_text, onAction }
- LoadingSkeleton: { rows }

### 14.6) UI 文案與錯誤碼對應（草案）

- AUTH_UNAUTHORIZED: "請先登入後再進行操作"
- CART_EMPTY: "購物車是空的，先去挑商品吧"
- INVENTORY_SHORTAGE: "庫存不足，已更新可購買數量"
- COUPON_INVALID: "優惠碼無效或已過期"
- PAYMENT_FAILED: "付款失敗，請重試或更換付款方式"
- ORDER_NOT_FOUND: "找不到訂單，請確認連結或重新整理"
- RATE_LIMITED: "操作過於頻繁，請稍後再試"
- NETWORK_ERROR: "連線異常，請稍後重試"

## 15) 待確認

- 物流服務（或自行出貨流程）
- 退貨/退款流程與權限
- 稅率/發票/多幣別需求
