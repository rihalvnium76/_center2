import java.math.BigDecimal;
import java.util.Collections;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SlotStringLite {

  private static final Pattern SLOT_PATTERN = Pattern.compile("\\{(.+?)}");

  public static String format(String template, Map<String, Object> values, StringBuffer buffer) {
    if (template == null || template.isEmpty()) {
      return "";
    }
    if (values == null) {
      values = Collections.emptyMap();
    }
    StringBuffer buffer0 = buffer;
    if (buffer0 == null) {
      buffer0 = new StringBuffer((int)(template.length() * 1.5F));
    }
    Matcher matcher = SLOT_PATTERN.matcher(template);
    while (matcher.find()) {
      String key = matcher.group(1);
      Object value = values.get(key);
      if (value == null) {
        value = "";
      } else if (value instanceof BigDecimal) {
        value = ((BigDecimal) value).toPlainString();
      }
      matcher.appendReplacement(buffer0, value.toString());
    }
    matcher.appendTail(buffer0);
    String ret = buffer0.toString();
    if (buffer != null) {
      buffer.setLength(0);
    }
    return ret;
  }
}
