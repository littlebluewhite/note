---
title: "Service Prompt"
category: prompt
tags: [prompt]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: note
status: active
---
# Service Prompt

要做一個websocket gateway service 規劃做法, 主要的功能是從各個後端service接kafka資料進來, 有一個檔案管控哪個websocket endpoint 接入哪幾個kafka的資料 ex: ws://api/v1/dashboard topic: alert, notification
前端拿到的資料就會是
{
	"topic": "alert",
	"data": {alert schema}
}

{
	"topic": "notification",
	"data": {notification schema}
}
先用sub agents 取得相關最新知識
