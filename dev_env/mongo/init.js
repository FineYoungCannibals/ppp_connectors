db = db.getSiblingDB('test_db');
db.test_collection.insertMany([
  { name: "Alice", role: "admin" },
  { name: "Bob", role: "user" }
]);
