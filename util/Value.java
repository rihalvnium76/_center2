import java.util.Map;
import java.util.function.Consumer;
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

    @SuppressWarnings("unchecked")
    public static <K, V> V get(Map<? extends K, ?> map, K key, V nullDefault) {
        V value;
        return map != null && (value = (V) map.get(key)) != null ? value : nullDefault;
    }

    public static <K, V> V get(Map<? extends K, ?> map, K key) {
        return get(map, key, null);
    }

    public static <T> T buildOf() {
        return null;
    }

    public static <T> T buildOf(T obj) {
        return obj;
    }

    public static <T> T buildOf(T obj, Consumer<T> builder) {
        builder.accept(obj);
        return obj;
    }

    public static <T> T buildOf(Supplier<T> builder) {
        return builder.get();
    }
}
