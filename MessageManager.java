import java.time.LocalDateTime;
import java.util.*;

public class MessageManager {

    // Queue for normal messages
    private Queue<Message> normalMessages;

    // PriorityQueue for delayed messages
    private PriorityQueue<Message> scheduledMessages;

    // HashMap for message lookup
    private HashMap<Integer, Message> messageMap;

    // ArrayList for message history
    private ArrayList<Message> messageHistory;

    public MessageManager() {

        normalMessages = new LinkedList<>();

        scheduledMessages = new PriorityQueue<>(
            Comparator.comparing(Message::getScheduledTime)
        );

        messageMap = new HashMap<>();

        messageHistory = new ArrayList<>();
    }

    // SEND normal message
    public void sendMessage(int id, String content) {

        if (messageMap.containsKey(id)) {
            System.out.println("Message ID already exists.");
            return;
        }

        Message message = new Message(
            id,
            content,
            "NORMAL",
            null
        );

        normalMessages.offer(message);

        messageMap.put(id, message);

        System.out.println("Message sent successfully.");
    }

    // SCHEDULE delayed message
    public void scheduleMessage(
            int id,
            String content,
            LocalDateTime scheduledTime) {

        if (messageMap.containsKey(id)) {
            System.out.println("Message ID already exists.");
            return;
        }

        Message message = new Message(
            id,
            content,
            "SCHEDULED",
            scheduledTime
        );

        scheduledMessages.offer(message);

        messageMap.put(id, message);

        System.out.println("Message scheduled successfully.");
    }

    // SEARCH message
    public void searchMessage(int id) {

        Message message = messageMap.get(id);

        if (message == null) {
            System.out.println("Message not found.");
        } else {
            System.out.println(message);
        }
    }

    // DISPLAY pending messages
    public void displayPendingMessages() {

        System.out.println("\n========== NORMAL MESSAGES ==========");

        if (normalMessages.isEmpty()) {
            System.out.println("No normal messages.");
        } else {

            for (Message message : normalMessages) {
                System.out.println(message);
            }
        }

        System.out.println("\n========== SCHEDULED MESSAGES ==========");

        if (scheduledMessages.isEmpty()) {
            System.out.println("No scheduled messages.");
        } else {

            for (Message message : scheduledMessages) {
                System.out.println(message);
            }
        }
    }

    // DELIVER next message
    public void deliverNextMessage() {

        LocalDateTime now = LocalDateTime.now();

        // Check scheduled message first
        if (!scheduledMessages.isEmpty()) {

            Message scheduledMessage =
                    scheduledMessages.peek();

            if (!scheduledMessage
                    .getScheduledTime()
                    .isAfter(now)) {

                scheduledMessages.poll();

                scheduledMessage.setStatus("DELIVERED");

                // Add to ArrayList
                messageHistory.add(scheduledMessage);

                // Save to file
                FileHandler.saveMessage(
                    scheduledMessage.toString()
                );

                System.out.println("\nMessage delivered:");
                System.out.println(scheduledMessage);

                return;
            }
        }

        // Deliver normal message
        if (!normalMessages.isEmpty()) {

            Message message = normalMessages.poll();

            message.setStatus("DELIVERED");

            // Add to ArrayList
            messageHistory.add(message);

            // Save to file
            FileHandler.saveMessage(
                message.toString()
            );

            System.out.println("\nMessage delivered:");
            System.out.println(message);

            return;
        }

        System.out.println("No message available for delivery.");
    }

    // CANCEL message
    public void cancelMessage(int id) {

        Message message = messageMap.get(id);

        if (message == null) {
            System.out.println("Message not found.");
            return;
        }

        if (!message.getStatus().equals("PENDING")) {
            System.out.println(
                "Message cannot be cancelled."
            );
            return;
        }

        // Remove from Queue
        normalMessages.remove(message);

        // Remove from PriorityQueue
        scheduledMessages.remove(message);

        message.setStatus("CANCELLED");

        // Add to ArrayList
        messageHistory.add(message);

        // Save to file
        FileHandler.saveMessage(
            message.toString()
        );

        System.out.println(
            "Message cancelled successfully."
        );
    }

    // DISPLAY history
    public void displayHistory() {

        System.out.println(
            "\n========== MESSAGE HISTORY =========="
        );

        if (messageHistory.isEmpty()) {
            System.out.println("No message history.");
            return;
        }

        for (Message message : messageHistory) {
            System.out.println(message);
        }
    }
}