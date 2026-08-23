import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        MessageManager manager = new MessageManager();

        DateTimeFormatter formatter =
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

        System.out.println("======================================");
        System.out.println("      MESSAGING SYSTEM WITH DELAY");
        System.out.println("======================================");

        System.out.println("\nAvailable Commands:");
        System.out.println("SEND <id> <message>");
        System.out.println("SCHEDULE <id> <date-time> <message>");
        System.out.println("SEARCH <id>");
        System.out.println("PENDING");
        System.out.println("DELIVER");
        System.out.println("CANCEL <id>");
        System.out.println("HISTORY");
        System.out.println("SAVED");
        System.out.println("EXIT");

        while (true) {

            System.out.print("\nEnter command: ");

            String input = scanner.nextLine().trim();

            if (input.isEmpty()) {
                continue;
            }

            String[] parts = input.split(" ", 3);

            String command = parts[0].toUpperCase();

            // SEND
            if (command.equals("SEND")) {

                if (parts.length < 3) {
                    System.out.println(
                        "Usage: SEND <id> <message>"
                    );
                    continue;
                }

                try {

                    int id = Integer.parseInt(parts[1]);

                    String message = parts[2];

                    manager.sendMessage(id, message);

                } catch (NumberFormatException e) {

                    System.out.println("Invalid message ID.");
                }
            }

            // SCHEDULE
            else if (command.equals("SCHEDULE")) {

                if (parts.length < 3) {
                    System.out.println(
                        "Usage: SCHEDULE <id> <date-time> <message>"
                    );
                    continue;
                }

                try {

                    int id = Integer.parseInt(parts[1]);

                    String remaining = parts[2];

                    /*
                     * Example:
                     *
                     * SCHEDULE 102 2026-08-22 20:00 Meeting
                     *
                     * remaining =
                     * 2026-08-22 20:00 Meeting
                     */

                    String dateTime =
                            remaining.substring(0, 16);

                    String message =
                            remaining.substring(17);

                    LocalDateTime scheduledTime =
                            LocalDateTime.parse(
                                dateTime,
                                formatter
                            );

                    manager.scheduleMessage(
                        id,
                        message,
                        scheduledTime
                    );

                } catch (Exception e) {

                    System.out.println(
                        "Invalid format."
                    );

                    System.out.println(
                        "Use: SCHEDULE 102 2026-08-22 20:00 Meeting"
                    );
                }
            }

            // SEARCH
            else if (command.equals("SEARCH")) {

                if (parts.length < 2) {

                    System.out.println(
                        "Usage: SEARCH <id>"
                    );

                    continue;
                }

                try {

                    int id = Integer.parseInt(parts[1]);

                    manager.searchMessage(id);

                } catch (NumberFormatException e) {

                    System.out.println("Invalid message ID.");
                }
            }

            // PENDING
            else if (command.equals("PENDING")) {

                manager.displayPendingMessages();
            }

            // DELIVER
            else if (command.equals("DELIVER")) {

                manager.deliverNextMessage();
            }

            // CANCEL
            else if (command.equals("CANCEL")) {

                if (parts.length < 2) {

                    System.out.println(
                        "Usage: CANCEL <id>"
                    );

                    continue;
                }

                try {

                    int id = Integer.parseInt(parts[1]);

                    manager.cancelMessage(id);

                } catch (NumberFormatException e) {

                    System.out.println("Invalid message ID.");
                }
            }

            // HISTORY
            else if (command.equals("HISTORY")) {

                manager.displayHistory();
            }

            // SAVED FILE HISTORY
            else if (command.equals("SAVED")) {

                FileHandler.displayFileHistory();
            }

            // EXIT
            else if (command.equals("EXIT")) {

                System.out.println(
                    "Exiting Messaging System..."
                );

                break;
            }

            else {

                System.out.println(
                    "Invalid command."
                );
            }
        }

        scanner.close();
    }
}
