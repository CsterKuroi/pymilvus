import datetime

from .types import DataType
from .constants import LOGICAL_BITS, LOGICAL_BITS_MASK

valid_index_types = [
    "FLAT",
    "IVF_FLAT",
    "IVF_SQ8",
    # "IVF_SQ8_HYBRID",
    "IVF_PQ",
    "HNSW",
    # "NSG",
    "ANNOY",
    "RHNSW_FLAT",
    "RHNSW_PQ",
    "RHNSW_SQ",
    "BIN_FLAT",
    "BIN_IVF_FLAT"
]

valid_index_params_keys = [
    "nlist",
    "m",
    "nbits",
    "M",
    "efConstruction",
    "PQM",
    "n_trees"
]

valid_binary_index_types = [
    "BIN_FLAT",
    "BIN_IVF_FLAT"
]

valid_binary_metric_types = [
    "JACCARD",
    "HAMMING",
    "TANIMOTO",
    "SUBSTRUCTURE",
    "SUPERSTRUCTURE"
]


def hybridts_to_unixtime(ts):
    physical = ts >> LOGICAL_BITS
    return physical / 1000.0


def mkts_from_hybridts(hybridts, milliseconds=0., delta=None):
    if not isinstance(milliseconds, (int, float)):
        raise Exception("parameter milliseconds should be type of int or float")

    if isinstance(delta, datetime.timedelta):
        milliseconds += (delta.microseconds / 1000.0)
    elif delta is not None:
        raise Exception("parameter delta should be type of datetime.timedelta")

    if not isinstance(hybridts, int):
        raise Exception("parameter hybridts should be type of int")

    logical = hybridts & LOGICAL_BITS_MASK
    physical = hybridts >> LOGICAL_BITS

    new_ts = int((int((physical + milliseconds)) << LOGICAL_BITS) + logical)
    return new_ts


def mkts_from_unixtime(epoch, milliseconds=0., delta=None):
    if not isinstance(epoch, (int, float)):
        raise Exception("parameter epoch should be type of int or float")

    if not isinstance(milliseconds, (int, float)):
        raise Exception("parameter milliseconds should be type of int or float")

    if isinstance(delta, datetime.timedelta):
        milliseconds += (delta.microseconds / 1000.0)
    elif delta is not None:
        raise Exception("parameter delta should be type of datetime.timedelta")

    epoch += (milliseconds / 1000.0)
    int_msecs = int(epoch * 1000 // 1)
    return int(int_msecs << LOGICAL_BITS)


def mkts_from_datetime(d_time, milliseconds=0., delta=None):
    if not isinstance(d_time, datetime.datetime):
        raise Exception("parameter d_time should be type of datetime.datetime")

    return mkts_from_unixtime(d_time.timestamp(), milliseconds=milliseconds, delta=delta)


def check_invalid_binary_vector(entities):
    for entity in entities:
        if entity['type'] == DataType.BINARY_VECTOR:
            if not isinstance(entity['values'], list) and len(entity['values']) == 0:
                return False
            else:
                dim = len(entity['values'][0]) * 8
                if dim == 0:
                    return False
                for values in entity['values']:
                    if len(values) * 8 != dim:
                        return False
                    if not isinstance(values, bytes):
                        return False
    return True


# def merge_results(results_list, topk, *args, **kwargs):
#     """
#     merge query results
#     """
#
#     def _reduce(source_ids, ids, source_diss, diss, k, reverse):
#         """
#
#         """
#         if source_diss[k - 1] <= diss[0]:
#             return source_ids, source_diss
#         if diss[k - 1] <= source_diss[0]:
#             return ids, diss
#
#         source_diss.extend(diss)
#         diss_t = enumerate(source_diss)
#         diss_m_rst = sorted(diss_t, key=lambda x: x[1], reverse=reverse)[:k]
#         diss_m_out = [id_ for _, id_ in diss_m_rst]
#
#         source_ids.extend(ids)
#         id_m_out = [source_ids[i] for i, _ in diss_m_rst]
#
#         return id_m_out, diss_m_out
#
#     status = common_pb2.Status(error_code=common_pb2.SUCCESS,
#                                reason="Success")
#
#     reverse = kwargs.get('reverse', False)
#     raw = kwargs.get('raw', False)
#
#     if not results_list:
#         return status, [], []
#
#     merge_id_results = []
#     merge_dis_results = []
#     row_num = 0
#
#     for files_collection in results_list:
#         if not isinstance(files_collection, Grpc_Result) and \
#                 not isinstance(files_collection, QueryResult):
#             return ParamError("Result type is unknown.")
#
#         row_num = files_collection.row_num
#         if not row_num:
#             continue
#
#         ids = files_collection.ids
#         diss = files_collection.distances  # distance collections
#         # Notice: batch_len is equal to topk, may need to compare with topk
#         batch_len = len(ids) // row_num
#
#         for row_index in range(row_num):
#             id_batch = ids[row_index * batch_len: (row_index + 1) * batch_len]
#             dis_batch = diss[row_index * batch_len: (row_index + 1) * batch_len]
#
#             if len(merge_id_results) < row_index:
#                 raise ValueError("merge error")
#             if len(merge_id_results) == row_index:
#                 merge_id_results.append(id_batch)
#                 merge_dis_results.append(dis_batch)
#             else:
#                 merge_id_results[row_index], merge_dis_results[row_index] = \
#                     _reduce(merge_id_results[row_index], id_batch,
#                             merge_dis_results[row_index], dis_batch,
#                             batch_len,
#                             reverse)
#
#     id_mrege_list = []
#     dis_mrege_list = []
#
#     for id_results, dis_results in zip(merge_id_results, merge_dis_results):
#         id_mrege_list.extend(id_results)
#         dis_mrege_list.extend(dis_results)
#
#     raw_result = Grpc_Result(
#         status=status,
#         row_num=row_num,
#         ids=id_mrege_list,
#         distances=dis_mrege_list
#     )
#
#     return raw_result if raw else QueryResult(raw_result, False)

def len_of(field_data) -> int:
    if field_data.HasField("scalars"):
        if field_data.scalars.HasField("bool_data"):
            return len(field_data.scalars.bool_data.data)
        elif field_data.scalars.HasField("int_data"):
            return len(field_data.scalars.int_data.data)
        elif field_data.scalars.HasField("long_data"):
            return len(field_data.scalars.long_data.data)
        elif field_data.scalars.HasField("float_data"):
            return len(field_data.scalars.float_data.data)
        elif field_data.scalars.HasField("double_data"):
            return len(field_data.scalars.double_data.data)
        elif field_data.scalars.HasField("string_data"):
            return len(field_data.scalars.string_data.data)
        elif field_data.scalars.HasField("bytes_data"):
            return len(field_data.scalars.bytes_data.data)
        else:
            raise BaseException("Unsupported scalar type")
    elif field_data.HasField("vectors"):
        dim = field_data.vectors.dim
        if field_data.vectors.HasField("float_vector"):
            total_len = len(field_data.vectors.float_vector.data)
            if total_len % dim != 0:
                raise BaseException(f"Invalid vector length: total_len={total_len}, dim={dim}")
            return int(total_len / dim)
        else:
            total_len = len(field_data.vectors.binary_vector)
            return int(total_len / (dim / 8))
    raise BaseException("Unknown data type")
