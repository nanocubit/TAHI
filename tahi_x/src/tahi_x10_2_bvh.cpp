#include <vector>
#include <array>
#include <cstdint>
#include <algorithm>

extern "C" {

struct Cell {
    int id;
    std::vector<int> ids;
    std::vector<float> pts;
    std::array<float, 5> lo, hi;
    int count;
};

struct BVHNode {
    std::array<float, 5> lo, hi;
    int first, last;
    int left, right;
    bool isLeaf() const { return left == -1; }
};

struct Index {
    std::vector<Cell> cells;
    std::vector<BVHNode> bvh;
};

static inline int cell_id(const float* p, int grid) {
    int id = 0;
    int multiplier = 1;
    for (int d = 0; d < 5; ++d) {
        int q = static_cast<int>(p[d] * grid);
        if (q >= grid) q = grid - 1;
        if (q < 0) q = 0;
        id += q * multiplier;
        multiplier *= grid;
    }
    return id;
}

static bool intersects(const std::array<float, 5>& lo,
                       const std::array<float, 5>& hi,
                       const float* a,
                       const float* b) {
    for (int d = 0; d < 5; ++d) {
        if (hi[d] < a[d] || lo[d] > b[d]) return false;
    }
    return true;
}

static void build_bvh(Index* index, int node, int first, int last) {
    auto& current = index->bvh[node];
    current.first = first;
    current.last = last;
    current.left = -1;
    current.right = -1;
    current.lo.fill(1.0f);
    current.hi.fill(0.0f);

    for (int i = first; i < last; ++i) {
        const auto& cell = index->cells[i];
        for (int d = 0; d < 5; ++d) {
            current.lo[d] = std::min(current.lo[d], cell.lo[d]);
            current.hi[d] = std::max(current.hi[d], cell.hi[d]);
        }
    }

    const int count = last - first;
    if (count <= 16) return;

    int axis = 0;
    float span = 0.0f;
    for (int d = 0; d < 5; ++d) {
        const float candidate = current.hi[d] - current.lo[d];
        if (candidate > span) {
            span = candidate;
            axis = d;
        }
    }

    std::sort(index->cells.begin() + first,
              index->cells.begin() + last,
              [axis](const Cell& a, const Cell& b) {
                  return (a.lo[axis] + a.hi[axis]) <
                         (b.lo[axis] + b.hi[axis]);
              });

    const int middle = first + count / 2;
    current.left = static_cast<int>(index->bvh.size());
    index->bvh.emplace_back();
    current.right = static_cast<int>(index->bvh.size());
    index->bvh.emplace_back();

    build_bvh(index, current.left, first, middle);
    build_bvh(index, current.right, middle, last);
}

void* tahi_build(const float* data, int n, int grid) {
    auto* index = new Index();
    const int total_cells = grid * grid * grid * grid * grid;
    std::vector<std::vector<int>> bins(total_cells);

    for (int i = 0; i < n; ++i) {
        bins[cell_id(data + 5LL * i, grid)].push_back(i);
    }

    index->cells.reserve(total_cells / 4);
    for (int id = 0; id < total_cells; ++id) {
        auto& object_ids = bins[id];
        if (object_ids.empty()) continue;

        Cell cell;
        cell.id = id;
        cell.count = static_cast<int>(object_ids.size());
        cell.ids = std::move(object_ids);
        cell.pts.resize(static_cast<size_t>(cell.count) * 5);
        cell.lo.fill(1.0f);
        cell.hi.fill(0.0f);

        for (int i = 0; i < cell.count; ++i) {
            const int object_id = cell.ids[i];
            for (int d = 0; d < 5; ++d) {
                const float value = data[object_id * 5 + d];
                cell.pts[i * 5 + d] = value;
                cell.lo[d] = std::min(cell.lo[d], value);
                cell.hi[d] = std::max(cell.hi[d], value);
            }
        }
        index->cells.push_back(std::move(cell));
    }

    bins.clear();
    bins.shrink_to_fit();
    if (!index->cells.empty()) {
        index->bvh.reserve(index->cells.size() * 2);
        index->bvh.emplace_back();
        build_bvh(index, 0, 0, static_cast<int>(index->cells.size()));
    }
    return index;
}

static void query_bvh(const Index* index, int node, const float* a,
                      const float* b, int* output, int& size) {
    const auto& current = index->bvh[node];
    if (!intersects(current.lo, current.hi, a, b)) return;

    if (current.isLeaf()) {
        for (int i = current.first; i < current.last; ++i) {
            const auto& cell = index->cells[i];
            if (!intersects(cell.lo, cell.hi, a, b)) continue;
            for (int j = 0; j < cell.count; ++j) {
                bool inside = true;
                for (int d = 0; d < 5; ++d) {
                    const float value = cell.pts[j * 5 + d];
                    if (value < a[d] || value > b[d]) {
                        inside = false;
                        break;
                    }
                }
                if (inside) output[size++] = cell.ids[j];
            }
        }
    } else {
        query_bvh(index, current.left, a, b, output, size);
        query_bvh(index, current.right, a, b, output, size);
    }
}

int tahi_query(void* handle, const float* a, const float* b, int* output) {
    auto* index = static_cast<Index*>(handle);
    if (index->bvh.empty()) return 0;
    int size = 0;
    query_bvh(index, 0, a, b, output, size);
    return size;
}

int tahi_cells(void* handle) {
    return static_cast<int>(static_cast<Index*>(handle)->cells.size());
}

void tahi_free(void* handle) {
    delete static_cast<Index*>(handle);
}

}
