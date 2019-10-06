import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

class ExperimentsResults:
    def __init__(self,
                 meta_data,
                 probas,
                 class_names,
                 meta_to_dataframes_func=None):
        """

        :param meta_data: 메타데이터
        :param probas: 확률값 2d array [n(row), classes]
        """
        orders = [i for i in range(len(probas))]
        self._class_names = class_names
        _probabilities = pd.DataFrame(probas, columns= class_names)
        _probabilities["order"] = orders

        idxes = ["order"]
        idxes.extend(class_names)
        _probabilities.set_index(idxes)

        if meta_to_dataframes_func is None:

            _meta_frames = self._meta_data_to_data_frames(meta_data)

        else:
            _meta_frames = meta_to_dataframes_func(meta_data)
        orders = [i for i in range(len(meta_data))]
        _meta_frames["order"] = orders
        _meta_frames.set_index(["order"])
        self._results = _meta_frames.merge(_probabilities, on="order")

    def _meta_data_to_data_frames(self, meta_data):
        cols = []
        rows = []
        if type(meta_data) is list:
            for idx, data in enumerate(meta_data):
                if idx == 0:
                    cols = [k for k in data]
                row = []
                for k in sorted(data.keys()):
                    row.append(data[k])
                rows.append(row)
            return pd.DataFrame(np.array(rows), columns=sorted(cols))
        elif type(meta_data) is dict:
            cols = [k for k in sorted(meta_data.keys())]
            rows = []
            data = meta_data
            for k in sorted(data.keys()):
                rows.append(data[k])
            return pd.DataFrame(rows, columns=cols)

    def to_csv(self, filename):
        self._results.to_csv(filename, mode="w")

    def results(self):
        return self._results

    def roc_curves(self,
                   true_label_name,
                   step=0.01,
                   group_by=None):
        # TPR
        # FAR = FP / TP + FP
        # FRR = FN / TN + FN
        group_lists = None
        if group_by is not None:
            group_lists = list(set(self._results[group_by].to_list()))


        threshold_count = len(list(np.arange(0.0, 1.0, step))) * len(self._class_names)
        if group_lists is not None and len(group_lists) != 0:
            threshold_count *= len(group_lists)


        if group_lists is not None and len(group_lists) != 0:
            tprfarfrr = np.zeros((threshold_count, 9 + len(group_lists)))
        else:
            tprfarfrr = np.zeros((threshold_count, 9))

        if group_lists is not None and len(group_lists) != 0:
            for idx, cur_group in enumerate(group_lists):
                target = self._results[self._results[group_by] == cur_group]
                tprfarfrr = self._cal_tprfarfrr(target, step, tprfarfrr, true_label_name, len(group_lists), idx, cur_group)
            return pd.DataFrame(tprfarfrr,
                                    columns=[group_by,"threshold", "label_index", "tpr", "far", "frr", "tp", "tn", "fp", "fn"])
        else:
            tprfarfrr = self._cal_tprfarfrr(self._results, step, tprfarfrr, true_label_name)

            return pd.DataFrame(tprfarfrr, columns=["threshold", "label_index" ,"tpr", "far", "frr", "tp", "tn", "fp", "fn"])

    def _cal_tprfarfrr(self, target_df, step, tprfarfrr, true_label_name, group_list_count=0, group_idx=0, current_group=None):
        total = len(list(np.arange(0.0, 1.0, step))) * len(self._class_names)
        for curidx, cur_thres in enumerate(np.arange(0.0, 1.0, step)):
            for select_idx, name in enumerate(self._class_names):
                expected = [1 - int(d) if select_idx == 0 else int(d) for d in target_df[true_label_name].to_list()]
                cur_df = target_df[target_df[name] >= cur_thres]
                cur_orders = cur_df["order"]

                actuals = [0 for _ in range(len(target_df))]
                for i in cur_orders:
                    actuals[i] = 1
                tn, fp, fn, tp = confusion_matrix(expected, actuals).ravel()
                tpr = tp / (tp + fn)
                far = fp / (fp + tn)
                frr = fn / (tp + fn)
                if group_list_count == 0:
                    tprfarfrr[curidx * len(self._class_names) + select_idx] = np.array(
                        [cur_thres, select_idx, tpr, far, frr, tp, tn, fp, fn], dtype=np.float32)
                else:
                    tprfarfrr[total * group_idx + curidx * len(self._class_names) + select_idx] = np.array(
                        [current_group, cur_thres, select_idx, tpr, far, frr, tp, tn, fp, fn], dtype=np.float32)
        return tprfarfrr
