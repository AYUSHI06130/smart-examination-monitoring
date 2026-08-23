import java.time.LocalDateTime;

public class Message {

    private int id;
    private String content;
    private String type;
    private LocalDateTime scheduledTime;
    private String status;

    public Message(int id, String content, String type,LocalDateTime scheduledTime) {

        this.id = id;
        this.content = content;
        this.type = type;
        this.scheduledTime = scheduledTime;
        this.status = "PENDING";
    }

    public int getId() {
        return id;
    }

    public String getContent() {
        return content;
    }

    public String getType() {
        return type;
    }

    public LocalDateTime getScheduledTime() {
        return scheduledTime;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    @Override
    public String toString() {

        if (scheduledTime != null) {
            return "ID: " + id +" | Message: " + content +" | Type: " + type +" | Scheduled: " + scheduledTime +" | Status: " + status;
        }

        return "ID: " + id +" | Message: " + content +" | Type: " + type +" | Status: " + status;
    }
}
