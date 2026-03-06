import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

k8s_concepts = [
    {
        "concept": "Pod",
        "description": """Pods are the smallest deployable units of computing that you can create and manage in Kubernetes.
A Pod (as in a pod of whales or pea pod) is a group of one or more containers, with shared storage and network resources, and a specification for how to run the containers.
A Pod's contents are always co-located and co-scheduled, and run in a shared context.
A Pod models an application-specific "logical host": it contains one or more application containers which are relatively tightly coupled.
In non-cloud contexts, applications executed on the same physical or virtual machine are analogous to cloud applications executed on the same logical host.
As well as application containers, a Pod can contain init containers that run during Pod startup.
You can also inject ephemeral containers for debugging a running Pod.""",
    },
    {
        "concept": "Service",
        "description": """Expose an application running in your cluster behind a single outward-facing endpoint, even when the workload is split across multiple backends.
In Kubernetes, a Service is a method for exposing a network application that is running as one or more Pods in your cluster.
A key aim of Services in Kubernetes is that you don't need to modify your existing application to use an unfamiliar service discovery mechanism.
You can run code in Pods, whether this is a code designed for a cloud-native world, or an older app you've containerized.
You use a Service to make that set of Pods available on the network so that clients can interact with it.
If you use a Deployment to run your app, that Deployment can create and destroy Pods dynamically.
From one moment to the next, you don't know how many of those Pods are working and healthy; you might not even know what those healthy Pods are named.
Kubernetes Pods are created and destroyed to match the desired state of your cluster.
Pods are ephemeral resources (you should not expect that an individual Pod is reliable and durable).
Each Pod gets its own IP address (Kubernetes expects network plugins to ensure this).
For a given Deployment in your cluster, the set of Pods running in one moment in time could be different from the set of Pods running that application a moment later.
This leads to a problem: if some set of Pods (call them "backends") provides functionality to other Pods (call them "frontends") inside your cluster, how do the frontends find out and keep track of which IP address to connect to, so that the frontend can use the backend part of the workload?
Enter Services.""",
    },
    {
        "concept": "Deployment",
        "description": """A Deployment manages a set of Pods to run an application workload, usually one that doesn't maintain state.
A Deployment provides declarative updates for Pods and ReplicaSets.
You describe a desired state in a Deployment, and the Deployment Controller changes the actual state to the desired state at a controlled rate.
You can define Deployments to create new ReplicaSets, or to remove existing Deployments and adopt all their resources with new Deployments.""",
    },
    {
        "concept": "ConfigMap",
        "description": """A ConfigMap is an API object used to store non-confidential data in key-value pairs.
Pods can consume ConfigMaps as environment variables, command-line arguments, or as configuration files in a volume.
A ConfigMap allows you to decouple environment-specific configuration from your container images, so that your applications are easily portable.""",
    },
    {
        "concept": "Secret",
        "description": """A Secret is an object that contains a small amount of sensitive data such as a password, a token, or a key.
Such information might otherwise be put in a Pod specification or in a container image.
Using a Secret means that you don't need to include confidential data in your application code.
Because Secrets can be created independently of the Pods that use them, there is less risk of the Secret (and its data) being exposed during the workflow of creating, viewing, and editing Pods.
Kubernetes, and applications that run in your cluster, can also take additional precautions with Secrets, such as avoiding writing sensitive data to nonvolatile storage.
Secrets are similar to ConfigMaps but are specifically intended to hold confidential data.""",
    },
]


def get_embedding(text):
    """Get embeddings from the sentence-transformers API"""
    response = requests.post("http://embeddings:8080/embed", json={"text": text})
    embedding = response.json()
    preview = [f"{x:.4f}" for x in embedding[:15]]
    print(f"Embedding vector for user input: [{', '.join(preview)}, ...]")
    return embedding


def setup_embedding_demo():
    print("\n🚀 Starting Simple Embeddings Demo...")

    print("🔤 Testing embedding service...")
    test_embedding = get_embedding("test")
    vector_size = len(test_embedding)

    print("📦 Connecting to Qdrant...")
    client = QdrantClient(host="qdrant", port=6333)
    collection_name = "k8s_concepts"

    try:
        client.delete_collection(collection_name)
    except:
        pass

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    print("\n💫 Creating embeddings for Kubernetes concepts...")

    for i, concept in enumerate(k8s_concepts):
        embedding = get_embedding(concept["description"])

        point = PointStruct(
            id=i,
            vector=embedding,
            payload={
                "concept": concept["concept"],
                "description": concept["description"],
            },
        )
        client.upsert(collection_name=collection_name, points=[point])
        print(f"✅ Stored: {concept['concept']}")

    print("\n🔍 Let's test our embeddings with a search...")
    query = "How can I store a password in Kubernetes?"
    print("\nQuery:", query)
    query_embedding = get_embedding(query)

    search_results = client.query_points(
        collection_name=collection_name, query=query_embedding, limit=2
    )

    print("\nTop 2 most relevant results:")
    for result in search_results.points:
        print(f"\n• {result.payload['concept']}:")
        print(f"  {result.payload['description']}")
        print(f"  Similarity score: {result.score:.4f}")


if __name__ == "__main__":
    setup_embedding_demo()
