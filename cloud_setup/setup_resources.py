from google.cloud import storage, pubsub_v1, firestore

# Set up project details
project_id = "dcsc-final-project-443518"
bucket_name_videos = "dcsc-final-project-bucket-videos-mava6837"
bucket_name_summaries = "dcsc-final-project-bucket-summaries-mava6837"
topic_name = "video-processing-tasks"
subscription_name = "video-processing-tasks-subscription"

# Initialize Google Cloud Clients
storage_client = storage.Client(project=project_id)
pubsub_client = pubsub_v1.PublisherClient()
subscriber_client = pubsub_v1.SubscriberClient()
firestore_client = firestore.Client(project=project_id)

# Create Cloud Storage Buckets
def create_bucket(bucket_name):
    try:
        bucket = storage_client.create_bucket(bucket_name)
        print(f"Created bucket {bucket_name}.")
    except Exception as e:
        if "409" in str(e):
            print(f"Bucket {bucket_name} already exists.")
        else:
            print(f"Error creating bucket {bucket_name}: {e}")

# Create Pub/Sub Topic and Subscription
def create_pubsub_resources():
    try:
        # Create topic
        topic_path = pubsub_client.topic_path(project_id, topic_name)
        try:
            topic = pubsub_client.create_topic(request={"name": topic_path})
            print(f"Created Pub/Sub topic {topic_name}.")
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                print(f"Pub/Sub topic {topic_name} already exists.")
            else:
                raise e
        
        # Create subscription
        subscription_path = subscriber_client.subscription_path(project_id, subscription_name)
        try:
            subscription = subscriber_client.create_subscription(request={
                "name": subscription_path,
                "topic": topic_path
            })
            print(f"Created Pub/Sub subscription {subscription_name}.")
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                print(f"Pub/Sub subscription {subscription_name} already exists.")
            else:
                raise e
    except Exception as e:
        print(f"Error creating Pub/Sub resources: {e}")

# Create Firestore Collection (Task Tracking)
def create_firestore_collection():
    try:
        collection_ref = firestore_client.collection("tasks")
        doc_ref, _ = collection_ref.add({
            "status": "initialized",
            "task_id": "example_task_1"
        })
        print(f"Firestore collection 'tasks' created with doc ID {doc_ref.id}.")
    except Exception as e:
        print(f"Error creating Firestore collection: {e}")

# Main function to run all resource creation
def setup_cloud_resources():
    create_bucket(bucket_name_videos)
    create_bucket(bucket_name_summaries)
    create_pubsub_resources()
    create_firestore_collection()

if __name__ == "__main__":
    setup_cloud_resources()
