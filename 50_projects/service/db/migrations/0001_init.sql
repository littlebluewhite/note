create extension if not exists pgcrypto;

create type user_status as enum ('active', 'disabled');
create type product_status as enum ('active', 'inactive', 'archived');
create type variant_status as enum ('active', 'inactive');
create type cart_status as enum ('active', 'checked_out', 'abandoned');
create type order_status as enum (
  'pending_payment',
  'paid',
  'preparing_shipment',
  'shipped',
  'completed',
  'payment_failed',
  'cancelled',
  'refund_requested',
  'refunded',
  'refund_rejected'
);
create type payment_status as enum ('created', 'pending', 'succeeded', 'failed', 'cancelled', 'refunded');
create type refund_status as enum ('requested', 'approved', 'processing', 'succeeded', 'rejected', 'failed');
create type shipment_status as enum ('pending', 'ready_to_ship', 'shipped', 'delivered', 'returned', 'cancelled');
create type coupon_type as enum ('fixed', 'percentage');
create type address_type as enum ('shipping', 'billing');
create type outbox_status as enum ('pending', 'processing', 'sent', 'failed', 'dead');

create table users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  password_hash text not null,
  status user_status not null default 'active',
  created_at timestamptz not null default now()
);

create table user_roles (
  user_id uuid not null references users(id) on delete cascade,
  role text not null,
  primary key (user_id, role)
);

create table abac_policies (
  id uuid primary key default gen_random_uuid(),
  subject text not null,
  resource text not null,
  action text not null,
  condition jsonb,
  created_at timestamptz not null default now()
);

create table products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  status product_status not null default 'active',
  created_at timestamptz not null default now()
);

create table product_variants (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references products(id) on delete cascade,
  sku text not null unique,
  price integer not null check (price >= 0),
  status variant_status not null default 'active'
);

create table product_images (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references products(id) on delete cascade,
  url text not null,
  sort_order integer not null default 0 check (sort_order >= 0)
);

create table categories (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  parent_id uuid references categories(id)
);

create table product_categories (
  product_id uuid not null references products(id) on delete cascade,
  category_id uuid not null references categories(id) on delete cascade,
  primary key (product_id, category_id)
);

create table inventory (
  id uuid primary key default gen_random_uuid(),
  variant_id uuid not null references product_variants(id) on delete cascade,
  qty_available integer not null default 0 check (qty_available >= 0),
  qty_reserved integer not null default 0 check (qty_reserved >= 0)
);

create table carts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  status cart_status not null default 'active',
  updated_at timestamptz not null default now()
);

create table cart_items (
  id uuid primary key default gen_random_uuid(),
  cart_id uuid not null references carts(id) on delete cascade,
  variant_id uuid not null references product_variants(id),
  qty integer not null check (qty > 0),
  price_snapshot integer not null check (price_snapshot >= 0)
);

create table orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id),
  status order_status not null default 'pending_payment',
  total integer not null check (total >= 0),
  currency text not null default 'TWD',
  created_at timestamptz not null default now()
);

create table order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  variant_id uuid not null references product_variants(id),
  qty integer not null check (qty > 0),
  price_snapshot integer not null check (price_snapshot >= 0)
);

create table order_addresses (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  type address_type not null,
  name text not null,
  phone text not null,
  address1 text not null,
  address2 text,
  city text not null,
  postal_code text not null
);

create table payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  provider text not null,
  status payment_status not null default 'created',
  amount integer not null check (amount >= 0),
  currency text not null default 'TWD',
  txn_id text,
  provider_ref text,
  created_at timestamptz not null default now()
);

create table refunds (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  payment_id uuid references payments(id),
  status refund_status not null default 'requested',
  amount integer not null check (amount >= 0),
  reason text,
  provider_ref text,
  created_at timestamptz not null default now()
);

create table shipments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  status shipment_status not null default 'pending',
  carrier text,
  tracking_no text,
  shipped_at timestamptz,
  delivered_at timestamptz
);

create table coupons (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  type coupon_type not null,
  value integer not null check (value >= 0),
  start_at timestamptz,
  end_at timestamptz
);

create table order_coupons (
  order_id uuid not null references orders(id) on delete cascade,
  coupon_id uuid not null references coupons(id),
  primary key (order_id, coupon_id)
);

create table event_outbox (
  id uuid primary key default gen_random_uuid(),
  aggregate_type text not null,
  aggregate_id uuid not null,
  event_type text not null,
  payload jsonb not null,
  status outbox_status not null default 'pending',
  attempts integer not null default 0 check (attempts >= 0),
  next_run_at timestamptz not null default now(),
  last_error text,
  created_at timestamptz not null default now()
);

create index idx_user_roles_role on user_roles(role);
create index idx_products_status on products(status);
create index idx_product_variants_product_id on product_variants(product_id);
create index idx_product_images_product_id on product_images(product_id);
create index idx_categories_parent_id on categories(parent_id);
create index idx_product_categories_product_id on product_categories(product_id);
create index idx_product_categories_category_id on product_categories(category_id);
create index idx_inventory_variant_id on inventory(variant_id);
create index idx_carts_user_id on carts(user_id);
create index idx_cart_items_cart_id on cart_items(cart_id);
create index idx_cart_items_variant_id on cart_items(variant_id);
create index idx_orders_user_id on orders(user_id);
create index idx_orders_status on orders(status);
create index idx_order_items_order_id on order_items(order_id);
create index idx_order_items_variant_id on order_items(variant_id);
create index idx_order_addresses_order_id on order_addresses(order_id);
create index idx_payments_order_id on payments(order_id);
create index idx_payments_status on payments(status);
create index idx_refunds_order_id on refunds(order_id);
create index idx_refunds_payment_id on refunds(payment_id);
create index idx_shipments_order_id on shipments(order_id);
create index idx_shipments_status on shipments(status);
create index idx_order_coupons_order_id on order_coupons(order_id);
create index idx_order_coupons_coupon_id on order_coupons(coupon_id);
create index idx_event_outbox_status_next on event_outbox(status, next_run_at);
create index idx_event_outbox_created_at on event_outbox(created_at);
