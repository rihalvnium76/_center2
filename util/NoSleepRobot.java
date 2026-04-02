import java.awt.*;
import java.awt.event.KeyEvent;
import java.util.Random;
import java.util.concurrent.atomic.AtomicBoolean;

public class NoSleepRobot {
  private final Robot robot;
  private final Random random;
  private final AtomicBoolean running;

  private NoSleepRobot(AtomicBoolean running) {
    robot = buildRobot();
    random = new Random();
    this.running = running;
  }

  public static void main(String[] args) {
    AtomicBoolean running = buildRunning();
    NoSleepRobot.create(running).start();
  }

  private static AtomicBoolean buildRunning() {
    AtomicBoolean running = new AtomicBoolean(true);
    Runtime.getRuntime().addShutdownHook(new Thread(() -> running.set(false)));
    return running;
  }

  public static NoSleepRobot create(AtomicBoolean running) {
    if (running == null) {
      running = new AtomicBoolean(true);
    }
    return new NoSleepRobot(running);
  }

  private Robot buildRobot() {
    Robot robot;
    try {
      robot = new Robot();
    } catch (AWTException e) {
      throw new RuntimeException(e);
    }
    robot.setAutoWaitForIdle(true);
    return robot;
  }

  public void start() {
    // check running
    pressKey(2000);
    pressKey(0);

    while (running.get()) {
      int pressCount = randomRange(1, 3);
      for (int i = 0; i < pressCount; i++) {
        // enable
        pressKey();
        // disable
        pressKey();
      }
      robot.delay(randomRange(5000, 10000));
    }
  }

  private void pressKey() {
    pressKey(randomRange(100, 250));
  }

  private void pressKey(int delayMs) {
    robot.keyPress(KeyEvent.VK_SCROLL_LOCK);
    robot.keyRelease(KeyEvent.VK_SCROLL_LOCK);
    robot.delay(delayMs);
  }

  private int randomRange(int min, int max) {
    return min + random.nextInt(max - min + 1);
  }
}
