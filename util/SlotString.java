import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;

public class SlotString {
  private static final Object TEXT_TYPE = new Object();
  private static final Object KEY_TYPE = new Object();

  private final StringBuilder res = new StringBuilder();
  private final StringBuilder key = new StringBuilder();
  private final ArrayList<String> texts;
  private final ArrayList<Object> types;

  public SlotString() {
    texts = null;
    types = null;
  }
  public SlotString(String pattern) {
    if (pattern == null || pattern.isEmpty()) {
      texts = null;
      types = null;
    } else {
      texts = new ArrayList<>();
      types = new ArrayList<>();
      compile(pattern);
    }
  }

  public String qformat(String pattern, Map<String, Object> vars) {
    if (pattern == null || pattern.isEmpty()) {
      return "";
    }
    if (vars == null) {
      parse(pattern, Collections.emptyMap());
    } else {
      parse(pattern, vars);
    }
    String ret = res.toString();
    res.setLength(0);
    key.setLength(0);
    return ret;
  }

  private void compile(String pattern) {
    parse(pattern, null);
    if (res.length() != 0) {
      texts.add(res.toString());
      types.add(TEXT_TYPE);
    }
    res.setLength(0);
    key.setLength(0);
    texts.trimToSize();
    types.trimToSize();
  }

  public String format(Map<String, Object> vars) {
    if (types == null || types.isEmpty()) {
      return "";
    }
    for (int i = 0; i < types.size(); ++i) {
      Object type = types.get(i);
      String text = texts.get(i);
      if (type == TEXT_TYPE) {
        res.append(text);
      } else if (type == KEY_TYPE) {
        String val = asString(vars, text);
        if (val != null && !val.isEmpty()) {
          res.append(val);
        }
      }
    }
    String ret = res.toString();
    res.setLength(0);
    return ret;
  }

  private void parse(String pattern, Map<String, Object> vars) {
    int state = 0;
    for (int i = 0; i < pattern.length(); ++i) {
      char c = pattern.charAt(i);
      if (state == 0) {
        if (c == '{') {
          state = 1;
        } else if (c == '\\') {
          state = 2;
        } else {
          res.append(c);
        }
      } else if (state == 1) {
        if (c == '}') {
          state = 0;
          if (vars == null) {
            parseCompile();
          } else {
            parseQformat(vars);
          }
        } else {
          key.append(c);
        }
      } else if (state == 2) {
        state = 0;
        res.append(c);
      }
    }
  }

  private void parseQformat(Map<String, Object> vars) {
    String val = asString(vars, key.toString());
    if (val != null && !val.isEmpty()) {
      res.append(val);
    }
    key.setLength(0);
  }

  private void parseCompile() {
    if (res.length() != 0) {
      texts.add(res.toString());
      types.add(TEXT_TYPE);
      res.setLength(0);
    }
    texts.add(key.toString());
    types.add(KEY_TYPE);
    key.setLength(0);
  }

  protected String asString(Map<String, Object> vars, String key) {
    Object val = vars.get(key);
    if (val == null) {
      return "";
    }
    if (val instanceof BigDecimal) {
      return ((BigDecimal) val).toPlainString();
    }
    return val.toString();
  }
}
