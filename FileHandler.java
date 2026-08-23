import java.io.*;

public class FileHandler {

    private static final String FILE_NAME = "message_history.txt";

    public static void saveMessage(String message) {

        try (FileWriter writer = new FileWriter(FILE_NAME, true)) {

            writer.write(message);
            writer.write(System.lineSeparator());

        } catch (IOException e) {

            System.out.println("Error saving message.");
        }
    }

    public static void displayFileHistory() {

        File file = new File(FILE_NAME);

        if (!file.exists()) {
            System.out.println("No saved history found.");
            return;
        }

        System.out.println("\n========== SAVED HISTORY ==========");

        try (BufferedReader reader =
                     new BufferedReader(new FileReader(FILE_NAME))) {

            String line;

            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

        } catch (IOException e) {

            System.out.println("Error reading history.");
        }
    }
}
