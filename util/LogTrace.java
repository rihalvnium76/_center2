import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;

public class LogTrace implements AutoCloseable {
  public static final String ID = "traceId";

  private final String prevId;

  public LogTrace(String traceId) {
    prevId = id();
    MDC.put(ID, traceId == null || traceId.isEmpty() ? randomString(16) : traceId);
  }

  public LogTrace() {
    this(id());
  }

  public static String id() {
    return MDC.get(ID);
  }

  public static <T> T call(String traceId, Callable<T> fn) {
    try (var ignored = new LogTrace(traceId)) {
      return fn.call();
    } catch (RuntimeException e) {
      throw e;
    } catch (Throwable e) {
      throw new RuntimeException(e.getMessage(), e);
    }
  }

  public static <T> T call(Callable<T> fn) {
    return call(id(), fn);
  }

  public static void run(String traceId, Runnable fn) {
    try (var ignored = new LogTrace(traceId)) {
      fn.run();
    }
  }

  public static void run(Runnable fn) {
    run(id(), fn);
  }

  public static String tag(String tagName) {
    return "[" + tagName + " " + id() + "]";
  }

  public static void setup(HttpServletResponse response) {
    response.setHeader("X-Trace-Id", id());
  }

  public static void clear() {
    MDC.remove(ID);
  }

  @Override
  public void close() {
    MDC.put(ID, prevId);
  }


  public static String randomString(int length, boolean secure) {
    final var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    var sb = new StringBuilder(length);
    var random = secure ? new SecureRandom() : ThreadLocalRandom.current();
    for (int i = 0; i < length; i++) {
      sb.append(chars.charAt(random.nextInt(chars.length())));
    }
    return sb.toString();
  }

  public static String randomString(int length) {
    return randomString(length, false);
  }

  // replace with the real MDC
  public interface MDC {
    ThreadLocal<Map<String, String>> ctx = ThreadLocal.withInitial(HashMap::new);
    static void put(String key, String value) { ctx.get().put(key, value); }
    static void remove(String key) { ctx.get().remove(key); }
    static String get(String key) { return ctx.get().get(key); }
    static void clear() { ctx.get().clear(); }
  }

  // replace with the read HttpServletResponse
  public interface HttpServletResponse {
    default void setHeader(String key, String value) {}
  }
}


