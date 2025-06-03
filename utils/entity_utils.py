import json
from bfabric_web_apps import get_logger, bfabric_interface

def extended_entity_data(token_data: dict) -> str:
    """
    This function takes in a token from B-Fabric and returns the entity data for the token.
    Edit this function to change which data is stored in the browser for this entity
    """

    entity_class_map = {
        "Run": "run",
        "Sample": "sample",
        "Project": "container",
        "Order": "container",
        "Container": "container",
        "Plate": "plate"
    }

    if not token_data:
        return None

    wrapper = bfabric_interface.get_wrapper()
    entity_class = token_data.get('entityClass_data')
    endpoint = entity_class_map.get(entity_class)
    entity_id = token_data.get('entity_id_data')
    jobId = token_data.get('jobId', None)
    username = token_data.get("user_data", "None")

    sample_lanes = {}

    if wrapper and entity_class and endpoint and entity_id:

        L = get_logger(token_data)

        entity_data_list = L.logthis(
            api_call=wrapper.read,
            endpoint=endpoint,
            obj={"id": entity_id},
            max_results=None,
            flush_logs = False
        )

        if not entity_data_list:
            return json.dumps({})
        entity_data_dict = entity_data_list[0]

        rununit_id = entity_data_dict.get("rununit", {}).get("id")
        if not rununit_id:
            return json.dumps({})

        #lane_data_list = wrapper.read(endpoint="rununit", obj={"id": str(rununit_id)}, max_results=None)

        lane_data_list = L.logthis(
                    api_call=wrapper.read,
                    endpoint="rununit",
                    obj={"id": str(rununit_id)},
                    max_results=None,
                    flush_logs = False
        )

        if not lane_data_list:
            return json.dumps({})
        lane_data = lane_data_list[0]

        #lane_samples = wrapper.read(endpoint="rununitlane", obj={"id": [str(elt["id"]) for elt in lane_data.get("rununitlane", [])]}, max_results=None)

        lane_samples = L.logthis(
            api_call=wrapper.read,
            endpoint="rununitlane",
            obj={"id": [str(elt["id"]) for elt in lane_data.get("rununitlane", [])]},
            max_results=None,
            flush_logs=False
        )

        for lane in lane_samples:
            samples = []
            sample_ids = [str(elt["id"]) for elt in lane.get("sample", [])]
            if len(sample_ids) < 100:
                
                #samples = wrapper.read(endpoint="sample", obj={"id": sample_ids}, max_results=None)
                samples = L.logthis(
                    api_call=wrapper.read,
                    endpoint="sample",
                    obj={"id": sample_ids},
                    max_results=None,
                    flush_logs=False
                )

            else:
                for i in range(0, len(sample_ids), 100):
                    
                    #samples += wrapper.read(endpoint="sample", obj={"id": sample_ids[i:i+100]}, max_results=None)
                    samples += L.logthis(
                        api_call=wrapper.read,
                        endpoint="sample",
                        obj={"id": sample_ids[i:i+100]},
                        max_results=None,
                        flush_logs=False
                    )

            container_ids = list(set([sample.get("container", {}).get("id") for sample in samples if sample.get("container")]))
            sample_lanes[str(lane.get("position"))] = [f"{container_id} {L.logthis(api_call=wrapper.read,endpoint='container', obj={'id': str(container_id)}, max_results=None, flush_logs=True )[0].get('name', '')}"
                                                       for container_id in container_ids
        ]
    else:
        L.flush_logs()
        return json.dumps({})

    json_data = {
        "name": entity_data_dict.get("name", ""),
        "createdby": entity_data_dict.get("createdby", ""),
        "created": entity_data_dict.get("created", ""),
        "modified": entity_data_dict.get("modified", ""),
        "lanes": sample_lanes,
        "containers": [container["id"] for container in entity_data_dict.get("container", []) if container.get("classname") == "order"],
        "server": entity_data_dict.get("serverlocation", ""),
        "datafolder": entity_data_dict.get("datafolder", "")
    }

    L.flush_logs()
    return json.dumps(json_data)