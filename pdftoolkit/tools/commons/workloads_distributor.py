from typing import Sequence, Any


def distribute_evenly(
    total: Sequence[Any], sub_seq_count: int
) -> Sequence[Sequence[Any]]:
    assert sub_seq_count > 0, "invalid argument: sub_seq_count <= 0"

    total_len = len(total)

    if sub_seq_count > total_len:
        sub_seq_count = total_len

    sub_seq_size = total_len // sub_seq_count
    remaining_elements = total_len % sub_seq_count

    sub_seqs = []

    start_idx = 0
    for i in range(sub_seq_count):
        sub_seq_len = sub_seq_size + (1 if i < remaining_elements else 0)
        sub_seq = total[start_idx : start_idx + sub_seq_len]
        sub_seqs.append(sub_seq)
        start_idx += sub_seq_len
    return sub_seqs
