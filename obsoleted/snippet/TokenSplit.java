package util.token_split;

import java.util.ArrayDeque;
import java.util.Objects;

public class TokenSplit {
  private Character mEscape;
  private String mWeakSeparators, mSeparators;
  private String mQuotes, mBrackets;
  private boolean mAllowUnknownEscape, mMergeDiffWeakSeparators;

  public Result parse(String str) {
    return new State(str).parse();
  }

  private static String avoidNullString(String str) {
    return str == null ? "" : str;
  }


  @Override
  public String toString() {
    return "TokenSplit{" +
      "mEscape=" + mEscape +
      ", mWeakSeparators='" + mWeakSeparators + '\'' +
      ", mSeparators='" + mSeparators + '\'' +
      ", mQuotes='" + mQuotes + '\'' +
      ", mBrackets='" + mBrackets + '\'' +
      ", mAllowUnknownEscape=" + mAllowUnknownEscape +
      ", mMergeDiffWeakSeparators=" + mMergeDiffWeakSeparators +
      '}';
  }

  public Character getEscape() {
    return mEscape;
  }

  public TokenSplit setEscape(Character escape) {
    mEscape = escape;
    return this;
  }

  public String getWeakSeparators() {
    return mWeakSeparators;
  }

  public TokenSplit setWeakSeparators(String weakSeparators) {
    mWeakSeparators = weakSeparators;
    return this;
  }

  public String getSeparators() {
    return mSeparators;
  }

  public TokenSplit setSeparators(String separators) {
    mSeparators = separators;
    return this;
  }

  public String getQuotes() {
    return mQuotes;
  }

  public TokenSplit setQuotes(String quotes) {
    mQuotes = quotes;
    return this;
  }

  public String getBrackets() {
    return mBrackets;
  }

  public TokenSplit setBrackets(String brackets) throws IllegalArgumentException {
    if (brackets.length() % 2 != 0) throw new IllegalArgumentException("Bracket must be paired");
    mBrackets = brackets;
    return this;
  }

  public boolean isAllowUnknownEscape() {
    return mAllowUnknownEscape;
  }

  public TokenSplit setAllowUnknownEscape(boolean allowUnknownEscape) {
    mAllowUnknownEscape = allowUnknownEscape;
    return this;
  }

  public boolean isMergeDiffWeakSeparators() {
    return mMergeDiffWeakSeparators;
  }

  public TokenSplit setMergeDiffWeakSeparators(boolean mergeDiffWeakSeparators) {
    mMergeDiffWeakSeparators = mergeDiffWeakSeparators;
    return this;
  }


  /**
   * result and remainder is NEVER null
   */
  public static class Result {
    private final Types mType;
    private final Character mLeftPair;
    private final String mResult;
    private final Character mRightPair;
    private final String mRemainder;
    private final ErrorCodes mErrorCode;

    public Result(Types type, Character leftPair, String result, Character rightPair, String remainder, ErrorCodes errorCode) {
      mType = type;
      mLeftPair = leftPair;
      mResult = result;
      mRightPair = rightPair;
      mRemainder = remainder;
      mErrorCode = errorCode;
    }
    public Result(Types type, String remainder, ErrorCodes errorCode) {
      this(type, null, "", null, remainder, errorCode);
    }
    public Result() {
      this(Types.TEXT, "", ErrorCodes.NO_ERROR);
    }


    @Override
    public String toString() {
      return "Result{" +
        "mType=" + mType +
        ", mLeftPair=" + mLeftPair +
        ", mResult='" + mResult + '\'' +
        ", mRightPair=" + mRightPair +
        ", mRemainder='" + mRemainder + '\'' +
        ", mErrorCode=" + mErrorCode +
        '}';
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) return true;
      if (!(o instanceof Result)) return false;
      Result result = (Result) o;
      return mType == result.mType && Objects.equals(mLeftPair, result.mLeftPair) && Objects.equals(mResult, result.mResult) && Objects.equals(mRightPair, result.mRightPair) && Objects.equals(mRemainder, result.mRemainder) && mErrorCode == result.mErrorCode;
    }

    @Override
    public int hashCode() {
      return Objects.hash(mType, mLeftPair, mResult, mRightPair, mRemainder, mErrorCode);
    }

    public Types getType() {
      return mType;
    }

    public Character getLeftPair() {
      return mLeftPair;
    }

    public String getResult() {
      return mResult;
    }

    public Character getRightPair() {
      return mRightPair;
    }

    public String getRemainder() {
      return mRemainder;
    }

    public ErrorCodes getErrorCode() {
      return mErrorCode;
    }


    public enum Types {
      TEXT, SEPARATOR, WEAK_SEPARATOR, QUOTE, BRACKET
    }

    public enum ErrorCodes {
      NO_ERROR, PAIR_MISMATCH_ERROR, UNKNOWN_ESCAPE_ERROR
    }
  }

  private class State {
    private final String mOrigin;
    private final int mLength;

    private int mPos = 0;
    private char mChr;
    private int mSymbolIndex = -1;

    private StringBuilder mResult;

    public State(String origin) {
      mOrigin = origin;
      mLength = origin == null ? 0 : origin.length();
    }

    public Result parse() {
      if (mLength == 0) return new Result();
      mResult = new StringBuilder(mLength);

      mChr = mOrigin.charAt(0);
      if (isBracket()) {
        if (mSymbolIndex % 2 == 0) {
          return parseBracket();
        } else return new Result(Result.Types.BRACKET, mOrigin, Result.ErrorCodes.PAIR_MISMATCH_ERROR);
      } else if (isQuote()) {
        return parseQuote();
      } else if (isSeparator()) {
        return new Result(Result.Types.SEPARATOR, null, String.valueOf(mChr), null, mOrigin.substring(mPos + 1), Result.ErrorCodes.NO_ERROR);
      } else if (isWeakSeparator()) {
        return parseWeakSeparator();
      } else return parseText();
    }

    private Result parseBracket() {
      ArrayDeque<Character> stack = new ArrayDeque<>();
      char lPair = mChr, rPair = mBrackets.charAt(mSymbolIndex + 1);

      stack.push(mChr);
      mainLoop:
      while (next()) {
        if (isEscape()) {
          if (!escape()) return new Result(Result.Types.BRACKET, mOrigin, Result.ErrorCodes.UNKNOWN_ESCAPE_ERROR);
        } else if (isQuote()) {
          mResult.append(mChr);
          for (char first = mChr; next(); ) {
            if (isEscape()) {
              if (!escape()) return new Result(Result.Types.BRACKET, mOrigin, Result.ErrorCodes.UNKNOWN_ESCAPE_ERROR);
            }
            mResult.append(mChr);
            if (mChr == first) continue mainLoop;
          }
          break;
        } else if (isBracket()) {
          if (mSymbolIndex % 2 == 0) {
            stack.push(mChr);
            mResult.append(mChr);
          } else {
            Character top = stack.peek();
            // Bracket pairing detection
            if (top != null && mBrackets.indexOf(top) == mSymbolIndex - 1) {
              stack.pop();
              if (stack.isEmpty()) {
                return new Result(Result.Types.BRACKET, lPair, mResult.toString(), rPair, mOrigin.substring(mPos + 1), Result.ErrorCodes.NO_ERROR);
              } else {
                mResult.append(mChr);
              }
            } else break;
          }
        } else { // TEXT
          mResult.append(mChr);
        }
      }
      return new Result(Result.Types.BRACKET, mOrigin, Result.ErrorCodes.PAIR_MISMATCH_ERROR);
    }
    private Result parseQuote() {
      for (char first = mChr; next(); ) {
        if (isEscape()) {
          if (!escape()) return new Result(Result.Types.QUOTE, mOrigin, Result.ErrorCodes.UNKNOWN_ESCAPE_ERROR);
        } if (mChr == first) {
          return new Result(Result.Types.QUOTE, first, mResult.toString(), first, mOrigin.substring(mPos + 1), Result.ErrorCodes.NO_ERROR);
        } else {
          mResult.append(mChr);
        }
      }
      return new Result(Result.Types.QUOTE, mOrigin, Result.ErrorCodes.PAIR_MISMATCH_ERROR);
    }
    private Result parseWeakSeparator() {
      mResult.append(mChr);
      for (char first = mChr; next() && (mMergeDiffWeakSeparators ? isWeakSeparator() : mChr == first); mResult.append(mChr)) ;
      return new Result(Result.Types.WEAK_SEPARATOR, null, mResult.toString(), null, mOrigin.substring(mPos), Result.ErrorCodes.NO_ERROR);
    }
    private Result parseText() {
      char first = mChr;
      do {
        if (isEscape()) {
          if (!escape()) return new Result(Result.Types.TEXT, mOrigin, Result.ErrorCodes.UNKNOWN_ESCAPE_ERROR);
        } else if (isSeparator() || isWeakSeparator() || isQuote() || isBracket()) {
          return new Result(Result.Types.TEXT, null, mResult.toString(), null, mOrigin.substring(mPos), Result.ErrorCodes.NO_ERROR);
        } else {
          mResult.append(mChr);
        }
      } while (next());
      return new Result(Result.Types.TEXT, null, mResult.toString(), null, "", Result.ErrorCodes.NO_ERROR);
    }

    private boolean next() {
      if (++mPos < mLength) {
        mChr = mOrigin.charAt(mPos);
        return true;
      } else return false;
    }

    private boolean escape() {
      if (next()) {
        if (isEscape() || isBracket() || isQuote() || isSeparator() || isWeakSeparator()) {
          mResult.append(mChr);
          return true;
        } else if (mAllowUnknownEscape) {
          mResult.append(mEscape).append(mChr); // CAN NOT mEscape+mChr
          return true;
        }
      }
      return false;
    }


    private boolean isEscape() {
      return Objects.equals(mEscape, mChr);
    }
    private boolean isSeparator() {
      mSymbolIndex = avoidNullString(mSeparators).indexOf(mChr);
      return mSymbolIndex != -1;
    }
    private boolean isWeakSeparator() {
      mSymbolIndex = avoidNullString(mWeakSeparators).indexOf(mChr);
      return mSymbolIndex != -1;
    }
    private boolean isQuote() {
      mSymbolIndex = avoidNullString(mQuotes).indexOf(mChr);
      return mSymbolIndex != -1;
    }
    private boolean isBracket() {
      mSymbolIndex = avoidNullString(mBrackets).indexOf(mChr);
      return mSymbolIndex != -1;
    }
  }
}
