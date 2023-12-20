# hello_milvus.py demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
# 1. connect to Milvus
# 2. create collection
# 3. insert data
# 4. create index
# 5. search, query, and hybrid search on entities
# 6. delete entities by PK
# 7. drop collection
import argparse
import os
import struct
import time

import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

from benchmark.hello_milvus import fmt


def test_hello_milvus():
    fmt = "\n=== {:30} ===\n"
    search_latency_fmt = "search latency = {:.4f}s"
    num_entities, dim = 3000, 8

    #################################################################################
    # 1. connect to Milvus
    # Add a new connection alias `default` for Milvus server in `localhost:19530`
    # Actually the "default" alias is a buildin in PyMilvus.
    # If the address of Milvus is the same as `localhost:19530`, you can omit all
    # parameters and call the method as: `connections.connect()`.
    #
    # Note: the `using` parameter of the following methods is default to "default".
    print(fmt.format("start connecting to Milvus"))
    connections.connect("default", host="localhost", port="19530")

    has = utility.has_collection("hello_milvus")
    print(f"Does collection hello_milvus exist in Milvus: {has}")

    #################################################################################
    # 2. create collection
    # We're going to create a collection with 3 fields.
    # +-+------------+------------+------------------+------------------------------+
    # | | field name | field type | other attributes |       field description      |
    # +-+------------+------------+------------------+------------------------------+
    # |1|    "pk"    |   VarChar  |  is_primary=True |      "primary field"         |
    # | |            |            |   auto_id=False  |                              |
    # +-+------------+------------+------------------+------------------------------+
    # |2|  "random"  |    Double  |                  |      "a double field"        |
    # +-+------------+------------+------------------+------------------------------+
    # |3|"embeddings"| FloatVector|     dim=8        |  "float vector with dim 8"   |
    # +-+------------+------------+------------------+------------------------------+
    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
        FieldSchema(name="random", dtype=DataType.DOUBLE),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]

    schema = CollectionSchema(fields, "hello_milvus is the simplest demo to introduce the APIs")

    print(fmt.format("Create collection `hello_milvus`"))
    hello_milvus = Collection("hello_milvus", schema, consistency_level="Strong")

    ################################################################################
    # 3. insert data
    # We are going to insert 3000 rows of data into `hello_milvus`
    # Data to be inserted must be organized in fields.
    #
    # The insert() method returns:
    # - either automatically generated primary keys by Milvus if auto_id=True in the schema;
    # - or the existing primary key field from the entities if auto_id=False in the schema.

    print(fmt.format("Start inserting entities"))
    rng = np.random.default_rng(seed=19530)
    entities = [
        # provide the pk field because `auto_id` is set to False
        [str(i) for i in range(num_entities)],
        rng.random(num_entities).tolist(),  # field random, only supports list
        rng.random((num_entities, dim)),  # field embeddings, supports numpy.ndarray and list
    ]

    insert_result = hello_milvus.insert(entities)

    hello_milvus.flush()
    print(f"Number of entities in Milvus: {hello_milvus.num_entities}")  # check the num_entities

    ################################################################################
    # 4. create index
    # We are going to create an IVF_FLAT index for hello_milvus collection.
    # create_index() can only be applied to `FloatVector` and `BinaryVector` fields.
    print(fmt.format("Start Creating index IVF_FLAT"))
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }

    hello_milvus.create_index("embeddings", index)

    ################################################################################
    # 5. search, query, and hybrid search
    # After data were inserted into Milvus and indexed, you can perform:
    # - search based on vector similarity
    # - query based on scalar filtering(boolean, int, etc.)
    # - hybrid search based on vector similarity and scalar filtering.
    #

    # Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
    print(fmt.format("Start loading"))
    hello_milvus.load()

    # -----------------------------------------------------------------------------
    # search based on vector similarity
    print(fmt.format("Start searching based on vector similarity"))
    vectors_to_search = entities[-1][-2:]
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    start_time = time.time()
    result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, output_fields=["random"])
    end_time = time.time()

    for hits in result:
        for hit in hits:
            print(f"hit: {hit}, random field: {hit.entity.get('random')}")
    print(search_latency_fmt.format(end_time - start_time))

    # -----------------------------------------------------------------------------
    # query based on scalar filtering(boolean, int, etc.)
    print(fmt.format("Start querying with `random > 0.5`"))

    start_time = time.time()
    result = hello_milvus.query(expr="random > 0.5", output_fields=["random", "embeddings"])
    end_time = time.time()

    print(f"query result:\n-{result[0]}")
    print(search_latency_fmt.format(end_time - start_time))

    # -----------------------------------------------------------------------------
    # pagination
    r1 = hello_milvus.query(expr="random > 0.5", limit=4, output_fields=["random"])
    r2 = hello_milvus.query(expr="random > 0.5", offset=1, limit=3, output_fields=["random"])
    print(f"query pagination(limit=4):\n\t{r1}")
    print(f"query pagination(offset=1, limit=3):\n\t{r2}")

    # -----------------------------------------------------------------------------
    # hybrid search
    print(fmt.format("Start hybrid searching with `random > 0.5`"))

    start_time = time.time()
    result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, expr="random > 0.5",
                                 output_fields=["random"])
    end_time = time.time()

    for hits in result:
        for hit in hits:
            print(f"hit: {hit}, random field: {hit.entity.get('random')}")
    print(search_latency_fmt.format(end_time - start_time))

    ###############################################################################
    # 6. delete entities by PK
    # You can delete entities by their PK values using boolean expressions.
    ids = insert_result.primary_keys

    expr = f'pk in ["{ids[0]}" , "{ids[1]}"]'
    print(fmt.format(f"Start deleting with expr `{expr}`"))

    result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
    print(f"query before delete by expr=`{expr}` -> result: \n-{result[0]}\n-{result[1]}\n")

    hello_milvus.delete(expr)

    result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
    print(f"query after delete by expr=`{expr}` -> result: {result}\n")

    ###############################################################################
    # 7. drop collection
    # Finally, drop the hello_milvus collection
    print(fmt.format("Drop collection `hello_milvus`"))
    utility.drop_collection("hello_milvus")


def fvecs_read_all(filename):
    vectors = []
    with open(filename, 'rb') as f:
        while True:
            try:
                dims = struct.unpack('i', f.read(4))[0]
                vec = struct.unpack('{}f'.format(dims), f.read(4 * dims))
                assert dims == len(vec)
                vectors.append(list(vec))
            except struct.error:
                break
    return vectors


def import_sift_1m_milvus(path):
    print(fmt.format("start connecting to Milvus"))
    connections.connect("default", host="localhost", port="19530")

    has = utility.has_collection("sift_benchmark")
    print(f"Does collection sift_benchmark exist in Milvus: {has}")

    num_entities, dim = 100_0000, 128
    fields = [
        FieldSchema(name="col1", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]
    schema = CollectionSchema(fields, "sift_1m is a collection for benchmark")
    sift_collection = Collection("sift_benchmark", schema, consistency_level="Strong")

    # import data
    print("Start importing data")
    vectors = fvecs_read_all(path)
    print(f"Number of entities: {len(vectors)}")

    entities = [
        vectors
    ]

    start = time.time()
    sift_collection.insert(entities)
    end = time.time()
    print(f"Time to insert {num_entities} entities: {end - start}")

    sift_collection.flush()
    print(f"Number of entities in Milvus: {sift_collection.num_entities}")


def import_gist_1m_milvus(path):
    num_entities, dim = 100_0000, 960
    fields = [
        FieldSchema(name="col1", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]
    schema = CollectionSchema(fields, "gist_1m is a collection for benchmark")
    gist_collection = Collection("gist_1m", schema, consistency_level="Strong")

    # import data
    print("Start importing data")
    vectors = fvecs_read_all(path)
    print(f"Number of entities: {len(vectors)}")

    entities = [
        vectors
    ]

    gist_collection.insert(entities)
    gist_collection.flush()

    print(f"Number of entities in Milvus: {gist_collection.num_entities}")


def import_data(path):
    if os.path.exists(path + "/sift_base.fvecs"):
        import_sift_1m_milvus(path + "/sift_base.fvecs")
    elif os.path.exists(path + "/gist_base.fvecs"):
        import_gist_1m_milvus(path + "/gist_base.fvecs")
    else:
        raise Exception("Invalid data set")


def benchmark(threads, rounds, data_set, path):
    import_data(path)
    if not os.path.exists(path):
        print(f"Path: {path} doesn't exist")
        raise Exception(f"Path: {path} doesn't exist")
    if data_set == "sift_1m":
        query_path = path + "/sift_query.fvecs"
        ground_truth_path = path + "/sift_groundtruth.ivecs"



    elif data_set == "gist_1m":
        query_path = path + "/gist_query.fvecs"
        ground_truth_path = path + "/gist_groundtruth.ivecs"
    else:
        raise Exception("Invalid data set")


if __name__ == '__main__':
    current_path = os.getcwd()
    parent_path = os.path.dirname(current_path)
    parent_path = os.path.dirname(parent_path)

    print(f"Current Path: {current_path}")
    print(f"Parent Path: {parent_path}")

    parser = argparse.ArgumentParser(description="Benchmark Infinity")

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        dest="threads",
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=5,
        dest="rounds",
    )
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        default='sift_1m',  # gist_1m
        dest="data_set",
    )

    data_dir = parent_path + "/test/data/benchmark/" + parser.parse_args().data_set
    print(f"Data Dir: {data_dir}")

    args = parser.parse_args()

    benchmark(args.threads, args.rounds, args.data_set, path=data_dir)