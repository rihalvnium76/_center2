package util.token_split;

public class TokenSplitTest {
  private TokenSplit ts = new TokenSplit();

  public static void main(String[] args) {
    new TokenSplitTest().start();
  }

  public void start() {
    ts.setEscape('\\').setWeakSeparators(" \t").setSeparators(",;").setQuotes("'\"").setBrackets("()[]{}<>")
      .setAllowUnknownEscape(true).setMergeDiffWeakSeparators(true);

    check(null, new TokenSplit.Result());
    check("", new TokenSplit.Result());
    check("aaa", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "aaa", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("aaa bbb", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "aaa", null, " bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("  aaa", new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, "  ", null, "aaa", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check(" \t aaa", new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " \t ", null, "aaa", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check(" \\t aaa", new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " ", null, "\\t aaa", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("\\taaa", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "\\taaa", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("aaa,bbb", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "aaa", null, ",bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check(",,bbb", new TokenSplit.Result(TokenSplit.Result.Types.SEPARATOR, null, ",", null, ",bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("a\\(bbb", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "a(bbb", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("\\(bbb", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "(bbb", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("(aaa)bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '(', "aaa", ')', "bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("[aaa]bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '[', "aaa", ']', "bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("([aaa])bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '(', "[aaa]", ')', "bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("((aaa))bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '(', "(aaa)", ')', "bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("('[aaa]') bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '(', "'[aaa]'", ')', " bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("('[aaa]' bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET,"('[aaa]' bbb", TokenSplit.Result.ErrorCodes.PAIR_MISMATCH_ERROR));
    check("('[aaa]) bbb", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET,"('[aaa]) bbb", TokenSplit.Result.ErrorCodes.PAIR_MISMATCH_ERROR));
    check("'aaa'bbb", new TokenSplit.Result(TokenSplit.Result.Types.QUOTE, '\'', "aaa", '\'', "bbb", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("'aaabbb", new TokenSplit.Result(TokenSplit.Result.Types.QUOTE, null, "", null, "'aaabbb", TokenSplit.Result.ErrorCodes.PAIR_MISMATCH_ERROR));
    check(")aaa", new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, null, "", null, ")aaa", TokenSplit.Result.ErrorCodes.PAIR_MISMATCH_ERROR));
    check("a\\(b", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "a(b", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("a\\xb", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "a\\xb", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));

    ts.setMergeDiffWeakSeparators(false).setAllowUnknownEscape(false);
    check("  \t aaa", new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, "  ", null, "\t aaa", TokenSplit.Result.ErrorCodes.NO_ERROR));
    check("\\x aaa", new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "", null, "\\x aaa", TokenSplit.Result.ErrorCodes.UNKNOWN_ESCAPE_ERROR));

    // Continuous test
    ts.setMergeDiffWeakSeparators(true);
    String ctstr = "( \t\"a b\" & a , b)";
    TokenSplit.Result rs = check(ctstr, new TokenSplit.Result(TokenSplit.Result.Types.BRACKET, '(', " \t\"a b\" & a , b", ')', "", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getResult(), new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " \t", null, "\"a b\" & a , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.QUOTE, '"', "a b", '"', " & a , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " ", null, "& a , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "&", null, " a , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " ", null, "a , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "a", null, " , b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " ", null, ", b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.SEPARATOR, null, ",", null, " b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.WEAK_SEPARATOR, null, " ", null, "b", TokenSplit.Result.ErrorCodes.NO_ERROR));
    rs = check(rs.getRemainder(), new TokenSplit.Result(TokenSplit.Result.Types.TEXT, null, "b", null, "", TokenSplit.Result.ErrorCodes.NO_ERROR));

    System.out.println("--PASSED ALL TESTS");
  }

  private TokenSplit.Result check(String str, TokenSplit.Result expectation) {
    TokenSplit.Result rs = ts.parse(str);
    assert rs.equals(expectation) : rs.toString();
    return rs;
  }
}
