`curl -X POST -F "file=@progit.pdf" http://localhost:9000/upload`


```curl -X POST \
  http://localhost:9000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Git?",
    "pdf_id": "progit.pdf",
    "chat_history": []
  }'
  
  
```
