# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============


class Pandas():
    def __init__(self):
        pass

    def loc_value_index(self, useFrame, locValue, typeString):
        outList = []
        copyList = []
        allRowName = useFrame.index
        for thisIndex in allRowName:
            if typeString=='=':
                thisCol = useFrame.loc[thisIndex, useFrame.loc[thisIndex, :]==locValue]
            elif typeString=='>':
                thisCol = useFrame.loc[thisIndex, useFrame.loc[thisIndex, :]>locValue]
            elif typeString=='<':
                thisCol = useFrame.loc[thisIndex, useFrame.loc[thisIndex, :]<locValue]
            if len(thisCol) == 0:
                continue
            else:
                for _ in thisCol.index:
                    if (thisIndex, _) not in copyList:
                        outList.append({thisIndex, _})
                        copyList.append({_, thisIndex})
        return outList
