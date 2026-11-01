---
layout: post
title: Recommend Sort
published: True
---

# 搜索排序配置

搜索排序参数位于全局配置文件 `~/.QuickUp/config-advanced.json` 的
`searchRankingOptions` 对象中。`general.searchRanking` 仍然是总开关。

## 参数

| 配置键                 | 默认值 | 说明                                        |
| ---------------------- | -----: | ------------------------------------------- |
| `halfLifeDays`         | `14.0` | 统计分数的衰减半衰期，单位为天              |
| `usageSaturation`      |  `2.0` | 使用分饱和参数                              |
| `minRuns`              |    `2` | 任务至少累计多少次运行才参与排序            |
| `minUsage`             | `0.25` | 使用分低于此值时视为无效，范围为 `0` 到 `1` |
| `eventDedupeMs`        | `5000` | 相同事件的去重窗口，单位为毫秒              |
| `maxTasks`             |  `300` | 统计文件最多保留的任务数                    |
| `maxQueries`           |  `100` | 统计文件最多保留的查询数                    |
| `maxHitsPerQuery`      |   `10` | 每个查询最多保留的任务配对数                |
| `queryMinHits`         |    `2` | 查询与任务至少命中多少次才产生亲和度        |
| `searchMaxShift`       |  `2.5` | 搜索结果的最大加权位移分                    |
| `searchSignalUsage`    |  `0.6` | 搜索信号中使用分的权重                      |
| `searchSignalAffinity` |  `0.4` | 搜索信号中查询亲和度的权重                  |
| `queryKeyMaxlen`       |   `64` | 统计键允许的最大查询词长度                  |

## 兼容与校验

- 缺少 `searchRankingOptions` 或其中的字段时，使用上表默认值；旧版配置无需手工升级。
- 非法数值使用对应默认值。正数参数不能小于等于 `0`；`eventDedupeMs` 可为 `0`；`minUsage` 必须在 `0` 到 `1` 之间。
- 排序配置在应用启动时读取一次并缓存。修改 `searchRankingOptions` 后需要重启 QuickUp 才会生效；`searchRanking` 总开关仍可在设置界面即时切换。
- 统计数据按工作区写入 `<工作区>/usage.txt`。

## 事件计数

运行任务时，如果带有普通搜索词，会同时累计任务使用分、查询分和“查询词到任务”的命中分。随后同一搜索词触发的搜索事件还会单独累计一次查询分；这是现有统计模型的行为。

---

# Search Sorting Configuration

The search sorting parameters are located in the global configuration file `~/.QuickUp/config-advanced.json` under the `searchRankingOptions` object. `general.searchRanking` remains the overall switch.

## Parameters

| Configuration Key      | Default Value | Description                                                  |
| ---------------------- | ------------- | ------------------------------------------------------------ |
| `halfLifeDays`         | `14.0`        | The decay half-life of the statistics score, in days         |
| `usageSaturation`      | `2.0`         | The usage saturation parameter                               |
| `minRuns`              | `2`           | The minimum number of cumulative runs for a task to participate in sorting |
| `minUsage`             | `0.25`        | If the usage fraction is below this value, it is considered invalid, ranging from `0` to `1` |
| `eventDedupeMs`        | `5000`        | The deduplication window for the same event, in milliseconds |
| `maxTasks`             | `300`         | The maximum number of tasks to retain for statistics files   |
| `maxQueries`           | `100`         | The maximum number of queries to retain for statistics files |
| `maxHitsPerQuery`      | `10`          | The maximum number of task pairs to retain per query         |
| `queryMinHits`         | `2`           | The minimum number of hits between a query and a task to generate affinity |
| `searchMaxShift`       | `2.5`         | The maximum weighted shift in search results                 |
| `searchSignalUsage`    | `0.6`         | The weight of the usage fraction in the search signal        |
| `searchSignalAffinity` | `0.4`         | The weight of the query affinity in the search signal        |
| `queryKeyMaxlen`       | `64`          | The maximum allowed length of query keywords for statistics keys |

## Compatibility and Validation

- When `searchRankingOptions` or its fields are missing, use the default values in the above table; the old configuration does not require manual upgrade.
- Illegal values use the corresponding default values. Positive parameters cannot be less than or equal to `0`; `eventDedupeMs` can be `0`; `minUsage` must be between `0` and `1`.
- The sorting configuration is read once when the application starts and cached. It will not be read again throughout the application lifecycle. After modifying `searchRankingOptions`, QuickUp needs to be restarted for the changes to take effect; the `searchRanking` overall switch can still be switched instantly in the settings interface.
- The statistics are written to `<workarea>/usage.txt` by the workspace.

## Event Counting

When running a task, if there is a common search term, the task usage points, query points, and "query term to task" hit points will be accumulated simultaneously. Subsequent search events triggered by the same search term will also accumulate one query point separately; this is the behavior of the existing statistical model.