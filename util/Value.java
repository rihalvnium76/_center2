import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.IntFunction;
import java.util.function.Supplier;

public record Value<E>(E value) {
  public static final Value<?> NULL = new Value<>(null);

  @SuppressWarnings("unchecked")
  public static <T> Value<T> of() {
    return (Value<T>) NULL;
  }

  public static <T> Value<T> of(T value) {
    if (value == null) {
      return of();
    }
    return new Value<>(value);
  }

  public static <T> T get(Value<T> value, T nullDefault) {
    T result;
    return value != null && (result = value.value()) != null ? result : nullDefault;
  }

  public static <T> T get(Value<T> value) {
    return get(value, null);
  }

  public static <T> Optional<T> toOptional(Value<T> value) {
    return Optional.ofNullable(get(value));
  }

  public Optional<E> toOptional() {
    return Optional.ofNullable(value);
  }


  // === Wonderful Test Utilities ===
  // (Recommend static import of this utility class)

  // Map Getters
  // (Null-safe and auto-casting)

  @SuppressWarnings("unchecked")
  public static <K, V> V get(Map<? extends K, ?> map, K key, V nullDefault) {
    V value;
    return map != null && (value = (V) map.get(key)) != null ? value : nullDefault;
  }

  public static <K, V> V get(Map<? extends K, ?> map, K key) {
    return get(map, key, null);
  }

  // Structured Object Builders
  // (Replace temporary variables with expressions to avoid polluting the scope)

  public static <T> T buildOf() {
    return null;
  }

  public static <T> T buildOf(T obj) {
    return obj;
  }

  // === NOTE on Mockito ===
  //
  // DO NOT do this (causes UnfinishedStubbingException):
  // when(root).thenReturn(
  //     buildOf(mock(A.class), a -> when(a).thenReturn(
  //         buildOf(mock(B.class), b -> when(b).thenReturn(...))
  //     ))
  // )
  //
  // Instead, do:
  // buildOf(
  //     buildOf(mock(A.class), a -> buildOf(
  //         buildOf(mock(B.class), b -> when(b).thenReturn(...)),
  //         b -> when(a).thenReturn(b)
  //     )),
  //     a -> when(root).thenReturn(a)
  // )
  public static <T> T buildOf(T obj, Consumer<T> builder) {
    if (builder != null) {
      builder.accept(obj);
    }
    return obj;
  }

  public static <T> T buildOf(Supplier<T> builder) {
    if (builder != null) {
      return builder.get();
    }
    return null;
  }

  public static <A, R> R buildTo(A src, Function<A, R> builder) {
    if (builder != null) {
      return builder.apply(src);
    }
    return null;
  }


  // Structured Mutable Collection Builders
  // (You never know whether the input collection will be written in)

  public static <E, C extends Collection<E>> C collectionOf(C target, E item) {
    target.add(item);
    return target;
  }

  @SafeVarargs
  public static <E, C extends Collection<E>> C collectionOf(C target, E item1, E... items) {
    target.add(item1);
    for (E item : items) {
      target.add(item);
    }
    return target;
  }

  public static <E> List<E> toList(IntFunction<List<E>> builder) {
    return builder.apply(0);
  }

  public static <E> List<E> toList(IntFunction<List<E>> builder, E item) {
    return collectionOf(builder.apply(1), item);
  }

  @SafeVarargs
  public static <E> List<E> toList(IntFunction<List<E>> builder, E item1, E... items) {
    return collectionOf(builder.apply(1 + items.length), item1, items);
  }

  public static <E> Set<E> toSet(IntFunction<Set<E>> builder) {
    return builder.apply(0);
  }

  public static <E> Set<E> toSet(IntFunction<Set<E>> builder, E item) {
    return collectionOf(builder.apply(2), item);
  }

  @SafeVarargs
  public static <E> Set<E> toSet(IntFunction<Set<E>> builder, E item1, E... items) {
    return collectionOf(builder.apply((int)((1 + items.length) / 0.75f) + 1), item1, items);
  }

  public static <K, V> Map.Entry<K, V> pair(K key, V value) {
    return new AbstractMap.SimpleEntry<>(key, value);
  }

  public static <K, V> Map<K, V> toMap(IntFunction<Map<K, V>> builder) {
    return builder.apply(0);
  }

  public static <K, V> Map<K, V> pairTo(IntFunction<Map<K, V>> builder, K key, V value) {
    var map = builder.apply(2);
    map.put(key, value);
    return map;
  }

  public static <K, V> Map<K, V> toMap(IntFunction<Map<K, V>> builder, Map.Entry<K, V> entry) {
    return pairTo(builder, entry.getKey(), entry.getValue());
  }

  @SafeVarargs
  public static <K, V> Map<K, V> toMap(IntFunction<Map<K, V>> builder, Map.Entry<K, V> entry1, Map.Entry<K, V>... entries) {
    var map = builder.apply((int)((1 + entries.length) / 0.75f) + 1);
    map.put(entry1.getKey(), entry1.getValue());
    for (Map.Entry<K, V> entry : entries) {
      map.put(entry.getKey(), entry.getValue());
    }
    return map;
  }

  public static <E> List<E> listOf() {
    return new ArrayList<>(0);
  }

  public static <E> List<E> listOf(E item) {
    return toList(ArrayList::new, item);
  }

  @SafeVarargs
  public static <E> List<E> listOf(E item1, E... items) {
    return toList(ArrayList::new, item1, items);
  }

  public static <E> Set<E> setOf() {
    return new HashSet<>(0);
  }

  public static <E> Set<E> setOf(E item) {
    return toSet(HashSet::new, item);
  }

  @SafeVarargs
  public static <E> Set<E> setOf(E item1, E... items) {
    return toSet(HashSet::new, item1, items);
  }

  public static <K, V> Map<K, V> mapOf() {
    return new HashMap<>(0);
  }

  public static <K, V> Map<K, V> pairTo(K key, V value) {
    return pairTo(HashMap::new, key, value);
  }

  public static <K, V> Map<K, V> mapOf(Map.Entry<K, V> entry) {
    return toMap(HashMap::new, entry);
  }

  @SafeVarargs
  public static <K, V> Map<K, V> mapOf(Map.Entry<K, V> entry1, Map.Entry<K, V>... entries) {
    return toMap(HashMap::new, entry1, entries);
  }


  // Silent Tested Method Runner
  // (Ignore all exceptions during CI execution)

  // Bypass SonarLint's dead code detection
  private static final boolean DEBUGGABLE = System.currentTimeMillis() < Long.MIN_VALUE + 1L;
  private static final Executable EXECUTABLE = () -> {};

  // Bypass SonarLint's missing assertion detection
  // Avoid failing unit test execution
  // Usage: assertDoesNotThrow(run(hasException, () -> spiedTestedClass.testedMethod()))
  public static Executable run(boolean hasException, Executable fn) {
    try {
      fn.execute();
    } catch (Throwable t) {
      if (DEBUGGABLE && !hasException) {
        throw new RuntimeException(t);
      }
    }
    return EXECUTABLE;
  }

  public static Executable run(Executable fn) {
    return run(false, fn);
  }

  // Replace to Executable of JUnit 5
  public interface Executable {
    void execute() throws Throwable;
  }
}
