from pymongo import MongoClient
from datetime import datetime
import json

client = MongoClient("mongodb://localhost:27017/")

# Check both databases
print("=" * 80)
print("DATABASE: facerecognition")
print("=" * 80)
db1 = client["facerecognition"]
for collection_name in db1.list_collection_names():
    count = db1[collection_name].count_documents({})
    print(f"  - {collection_name}: {count} documents")

print("\n" + "=" * 80)
print("DATABASE: facerecognition_db (OLD)")
print("=" * 80)
db2 = client["facerecognition_db"]
for collection_name in db2.list_collection_names():
    count = db2[collection_name].count_documents({})
    print(f"  - {collection_name}: {count} documents")

# Check for records in old database
old_attendance = list(db2["attendance_records"].find())
if old_attendance:
    print(f"\n⚠️ Found {len(old_attendance)} records in OLD database (facerecognition_db)")
    print("Migrating records to new database (facerecognition)...")
    
    db1["attendance_records"].insert_many(old_attendance)
    print(f"✅ Migrated {len(old_attendance)} records successfully!")
    
    # Clean up old database
    db2["attendance_records"].delete_many({})
    print("✅ Cleaned up old database")
else:
    print("\n✅ No records to migrate")
