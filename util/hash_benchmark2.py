import hashlib
from random import Random
import sys
import time
from typing import Any, Callable, Protocol
import xxhash


DATA_SIZE = 1024 * 1024 * 50
ITERATIONS = 10
TEXT_LINE_SEPARATOR_LENGTH = 52

class Hasher(Protocol):
    name: str
    def prepare(self): ...
    def update(self): ...
    def digest(self): ...
    def reset(self): ...

class HashlibHasher:
    def __init__(self, name: str, hasher: Any, data: bytes, digest: Callable[[Any], None]) -> None:
        self.name = name
        self._hasher = hasher
        self._data = data
        self._digest = digest

    @classmethod
    def from_name(cls, algorithm_name: str, data: bytes):
        if algorithm_name.startswith("shake"):
            length = 32
            digest = lambda hasher: hasher.digest(length)
        else:
            length = None
            digest = lambda hasher: hasher.digest()
            
        return cls(
            name=f"{algorithm_name}{f" ({length})" if length is not None else ""}",
            hasher=lambda: hashlib.new(algorithm_name),
            data=data,
            digest=digest,
        )
    
    def prepare(self):
        self._hasher = self._hasher()
        self._original = self._hasher.copy()
        # 预热（避免冷启动影响）
        self.update()
        self.digest()
        self.reset()

    def update(self):
        self._hasher.update(self._data)

    def digest(self):
        self._digest(self._hasher)

    def reset(self):
        self._hasher = self._original.copy()

    def __str__(self) -> str:
        return self.name

class XXHashHasher:
    def __init__(self, name: str, hasher: Any, data: bytes) -> None:
        self.name = name
        self._hasher = hasher
        self._data = data
    
    @classmethod
    def from_name(cls, algorithm_name: str, data: bytes):    
        return cls(
            name=algorithm_name,
            hasher=getattr(xxhash, algorithm_name),
            data=data,
        )
    
    def prepare(self):
        self._hasher = self._hasher()
        self._original = self._hasher.copy()
        # 预热（避免冷启动影响）
        self.update()
        self.digest()
        self.reset()

    def update(self):
        self._hasher.update(self._data)

    def digest(self):
        self._hasher.digest()

    def reset(self):
        self._hasher.reset()
        # self._hasher = self._original.copy()

    def __str__(self) -> str:
        return self.name


def benchmark_hash(data: bytes, hasher: Hasher, iterations: int):
    try:
        hasher.prepare()

        start = time.perf_counter()
        for _ in range(iterations):
            hasher.update()
            hasher.digest()
            hasher.reset()
        end = time.perf_counter()

        return end - start
    except Exception as e:
        print(f"  {hasher.name} 算法测试出错:", e)
        return None

def random_bytes(length: int, rnd: Random):
    return bytes(rnd.getrandbits(8) for _ in range(length))

def collect_algorithms(test_data: bytes):
    algorithms: set[Hasher] = set()
    for algorithm in hashlib.algorithms_available:
        algorithms.add(HashlibHasher.from_name(algorithm, test_data))
    for algorithm in xxhash.algorithms_available:
        algorithms.add(XXHashHasher.from_name(algorithm, test_data))
    return sorted(algorithms, key=lambda hasher: hasher.name)

def benchmark_all_algorithms(data_size=DATA_SIZE, iterations=ITERATIONS):
    print("正在准备测试数据 ...")
    prepare_start = time.perf_counter()
    test_data = random_bytes(data_size, Random("hash_benchmark_v2"))
    prepare_end = time.perf_counter()
    print(f"  - 完成，耗时 {prepare_end - prepare_start:>.1f} 秒")
    
    print("正在收集可用算法 ...")
    algorithms = collect_algorithms(test_data)
    algorithms_count = len(algorithms)

    print("=" * TEXT_LINE_SEPARATOR_LENGTH)
    print(f"测试数据大小: {data_size} 字节")
    print(f"迭代次数: {iterations}")
    print(f"Python版本: {sys.version.split()[0]}")
    print(f"可用的哈希算法数量: {algorithms_count}")
    print("=" * TEXT_LINE_SEPARATOR_LENGTH)

    total_start = time.perf_counter()

    results = []
    for i, algorithm in enumerate(algorithms):
        print(f"正在测试 {algorithm.name} 算法（{i + 1}/{algorithms_count}）...")
        duration = benchmark_hash(test_data, algorithm, iterations)
        if duration is not None and duration > 0:
            # 计算速度（MiB/s）
            total_data_processed = data_size * iterations
            speed_mbps = (total_data_processed / (1024 * 1024)) / duration
            
            results.append({
                'algorithm': algorithm.name,
                'time': duration,
                'speed': speed_mbps
            })

    # 按速度从快到慢排序
    results.sort(key=lambda x: x['speed'], reverse=True)
    
    total_end = time.perf_counter()
    
    # 打印结果
    print("=" * TEXT_LINE_SEPARATOR_LENGTH)
    print(f"{'算法名称':<10} {'耗时(秒)':>9} {'速度(MiB/s)':>10} {'相对性能':>6}")
    print("-" * TEXT_LINE_SEPARATOR_LENGTH)
    
    if results:
        fastest_speed = results[0]['speed']
        for result in results:
            relative_perf = result['speed'] / fastest_speed * 100
            print(f"{result['algorithm']:<14} {result['time']:>12.4f} "
                  f"{result['speed']:>12.2f} {relative_perf:>8.1f}%")
        
        # 打印最快的几个算法
        print("=" * TEXT_LINE_SEPARATOR_LENGTH)
        print(f"第一名: {results[0]['algorithm']} "
              f"({results[0]['speed']:.2f} MiB/s)")
        
        if len(results) >= 3:
            print(f"第二名: {results[1]['algorithm']} "
                  f"({results[1]['speed']:.2f} MiB/s)")
            print(f"第三名: {results[2]['algorithm']} "
                  f"({results[2]['speed']:.2f} MiB/s)")
        
        total_duration = total_end - total_start
        print(f"\n总耗时(秒): {total_duration}")
        
    else:
        print("没有成功测试任何算法")

if __name__ == "__main__":
    benchmark_all_algorithms()
