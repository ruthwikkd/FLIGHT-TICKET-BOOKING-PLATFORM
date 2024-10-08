import csv
import time
import smtplib
import ssl
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from reportlab.pdfgen import canvas




def get_current_date():
    now = time.localtime(time.time())
    return time.strftime("%Y-%m-%d", now)


def display_available_flights(rows, user_input1, user_input2):
    print(f"Available flights from {user_input1} to {user_input2} are:")
    for row in rows:
        if row[2] == user_input1 and row[3] == user_input2 and int(row[10]) > 0:
            print(
                f"{row[0]} - {row[4]}\n   Date: {row[1]}\n   Flight ID: {row[11]}\n   Price: {row[9]}")


def save_booking_to_file(user_input1, user_input2, FID, num_seats, user_name, user_phone):
    ticket_no = random.randint(1000, 9999)
    with open("booking_history.txt", "a") as booking_file:
        booking_file.write("Booking Details:\n")
        booking_file.write(f"Source: {user_input1}\n")
        booking_file.write(f"Destination: {user_input2}\n")
        booking_file.write(f"Flight ID: {FID}\n")
        booking_file.write(f"Number of Seats: {num_seats}\n")
        booking_file.write(f"Booking Time: {get_current_date()}\n")
        booking_file.write(f"Passenger Name: {user_name}\n")
        booking_file.write(f"Passenger Phone: {user_phone}\n")
        booking_file.write(f"Ticket ID: {ticket_no}\n\n")
    return ticket_no


def read_booked_tickets_from_file():
    booked_tickets = {}
    try:
        with open("booked_tickets.txt", "r") as file:
            for line in file:
                ticket_id, details = line.strip().split(':', 1)
                booked_tickets[int(ticket_id)] = eval(details)
    except FileNotFoundError:
        pass  
    return booked_tickets


def write_booked_tickets_to_file(booked_tickets):
    with open("booked_tickets.txt", "w") as file:
        for ticket_id, details in booked_tickets.items():
            file.write(f"{ticket_id}:{details}\n")


def cancel_ticket(booked_tickets, ticket_id, sender_email, app_password):
    ticket_found = False
    canceled_details = {}

    if ticket_id in booked_tickets or str(ticket_id) in booked_tickets:
        ticket_found = True
        canceled_details = booked_tickets[ticket_id]
        del booked_tickets[ticket_id]
        write_booked_tickets_to_file(booked_tickets)  # Update the file after cancellation
        print(f"Ticket ID {ticket_id} cancelled successfully.")
    else:
        print(f"Ticket ID {ticket_id} not found in the booked tickets.")

    return ticket_found, canceled_details


def display_booked_tickets():
    booked_tickets = read_booked_tickets_from_file()
    if not booked_tickets:
        print("No tickets have been booked.")
    else:
        print("Booked Tickets:")
        for ticket_id, details in booked_tickets.items():
            print(f"Ticket ID: {ticket_id}\n{details}\n")

def send_feedback_email(feedback, sender_email, sender_password):
    receiver_email = "aerobookmrt@gmail.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Feedback from User"

    body = f"User Email: {sender_email}\nFeedback:\n{feedback}"
    message.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Feedback sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP Authentication Error. Please check your email and password.")
    except Exception as e:
        print(f"Error sending feedback: {e}")

def send_thank_you_email(to_email, sender_email, app_password):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.starttls()

    try:
        smtp_obj.login(sender_email, app_password)

        subject = "Thank You for Your Booking"
        body = "Dear Passenger,\n\nThank you for booking your ticket with Aerobook! We appreciate your business.\n\nBest regards,\nThe Aerobook Team"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        smtp_obj.sendmail(sender_email, to_email, msg.as_string())
        print(f"Thank-you email sent successfully to {to_email}!")

    except Exception as e:
        print(f"Error sending thank-you email: {e}")

    finally:
        smtp_obj.quit()

def send_thank_you_email(to_email, sender_email, app_password, is_feedback=False):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.starttls()

    try:
        smtp_obj.login(sender_email, app_password)

        subject = "Thank You for Your Feedback" if is_feedback else "Thank You for Your Booking"
        body = "Dear Passenger,\n\nThank you for giving feedback! We are happy for your support.\n\nBest regards,\nThe Aerobookmrt Team"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        smtp_obj.sendmail(sender_email, to_email, msg.as_string())
        print(f"Thank-you email sent successfully to {to_email}!")

    except Exception as e:
        print(f"Error sending thank-you email: {e}")

    finally:
        smtp_obj.quit()


def create_pdf(booking_details, flight_details, user_name, user_phone, ticket_no):
    pdf_filename = f"ticket_{ticket_no}.pdf"

    c = canvas.Canvas(pdf_filename)
    c.drawString(100, 800, f"Ticket No: {ticket_no}")
    c.drawString(100, 780, f"Passenger Name: {user_name}")
    c.drawString(100, 760, f"Passenger Phone: {user_phone}")

    c.drawString(100, 740, "Booking Details:")
    booking_details_lines = booking_details.split('\n')
    for idx, line in enumerate(booking_details_lines):
        c.drawString(120, 720 - idx * 20, line)

    c.drawString(100, 640 - len(booking_details_lines) * 20, "Flight Details:")
    flight_details_lines = flight_details.split('\n')
    for idx, line in enumerate(flight_details_lines):
        c.drawString(120, 620 - (len(booking_details_lines) + idx) * 20, line)

    
    watermark_text = "AERBOOKMRT"
    c.setFont("Helvetica", 10)  
    c.setFillGray(0.7)  

    
    c.drawString(150, 400, watermark_text)

    
    c.saveState()
    c.rotate(90)
    c.drawString(450, -150, watermark_text)
    c.restoreState()

    c.save()

    print(f"PDF ticket generated: {pdf_filename}")
    return pdf_filename


def send_confirmation_email(to_email, sender_email, app_password, booking_details, flight_details, user_name, user_phone,
                            ticket_no):
    email_subject = "Aerobook - Booking Confirmation"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = email_subject

    email_body = f"Dear {user_name},\n\nThank you for booking your ticket with Aerobook! Your booking is confirmed.\n\nBooking Details:\n{booking_details}\n\nFlight Details:\n{flight_details}\n\nPassenger Name: {user_name}\nPassenger Phone: {user_phone}\n\nHave a safe journey!\n\nBest regards,\nAerobook Team"

    message.attach(MIMEText(email_body, "plain"))

    try:
        pdf_filename = create_pdf(booking_details, flight_details, user_name, user_phone, ticket_no)

        with open(pdf_filename, "rb") as pdf_file:
            pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            message.attach(pdf_attachment)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, message.as_string())
        print(f"Email sent successfully to {to_email}!")

    except Exception as e:
        print(f"Error sending email: {e}")

def send_cancelation_email(to_email, sender_email, app_password, ticket_id, canceled_details):
    email_subject = "Aerobook - Ticket Cancellation"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = email_subject

    email_body = f"Dear Passenger,\n\nYour ticket with Ticket ID {ticket_id} has been canceled.\n\nCancellation Details:\n{canceled_details}\n\nIf you have any concerns, feel free to contact us.\n\nBest regards,\nAerobook Team"

    message.attach(MIMEText(email_body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, message.as_string())
        print(f"Cancellation email sent successfully to {to_email}!")

    except Exception as e:
        print(f"Error sending cancellation email: {e}")

def main():
    with open("flights.csv", newline='') as file:
        rows = list(csv.reader(file))

    user_input1 = ""
    user_input2 = ""
    user_input3 = ""
    user_name = ""
    user_phone = ""

    sender_email = "aerobookmrt@gmail.com"
    app_password = "xxxx xxxx xxxx xxxx"

    option = None

    while option != 0:
        print("\nOptions:")
        print("1. Book a Ticket")
        print("2. View Available Flights")
        print("3. Provide Feedback")
        print("4. Cancel Ticket")
        print("0. Exit")
        option = int(input("Enter your choice: "))

        if option == 1:
            user_input3 = input("Enter Date (YYYY-MM-DD): ")
            current_date = get_current_date()
            found = False

            if user_input3 >= current_date:
                user_input1 = input("Enter Source Station: ")
                user_input2 = input("Enter Destination: ")
                user_name = input("Enter Passenger Name: ")
                user_phone = input("Enter Passenger Phone: ")

                print(f"The routes from {user_input1} to {user_input2} are")

                count = 0
                for row in rows:
                    if row[2] == user_input1 and row[3] == user_input2:
                        count += 1
                        print(
                            f"{count}) {row[4]}\n   Date of the journey: {row[1]}\n   Flight ID: {row[11]}\n   Arrival Time: {row[5]}\n   Departure Time: {row[6]}\n   No of Stops: {row[8]}\n   No of Seats: {row[10]}\n   Price: {row[9]}")
                        found = True

                if not found:
                    print(f"No match found for the input {user_input1} and {user_input2}")
            else:
                print("The provided date is not a valid date.")

            if found:
                FID = int(input("Enter your Flight ID: "))
                num_seats = int(input("Enter the number of seats you want to book: "))

                for row in rows:
                    if row[2] == user_input1 and row[3] == user_input2 and int(row[11]) == FID:
                        available_seats = int(row[10])
                        if num_seats <= available_seats:
                            row[11] = str(int(row[11]) - 1)
                            found = True
                            ticket_id = random.randint(100000, 999999)
                            booked_tickets = read_booked_tickets_from_file()
                            booked_tickets[ticket_id] = {
                                'user_input1': user_input1,
                                'user_input2': user_input2,
                                'FID': FID,
                                'num_seats': num_seats,
                                'user_name': user_name,
                                'user_phone': user_phone,
                                'booking_time': get_current_date()
                            }
                            print(
                                f"Booking Successful of {num_seats} seat(s) for the flight from {user_input1} to {user_input2} in {row[0]} flight\nFlight ID: {FID}\nTicket ID: {ticket_id}\nThanks for visiting")
                            print("Aerobook")
                            write_booked_tickets_to_file(booked_tickets)  

                            booking_details = f"\nSource: {user_input1}\nDestination: {user_input2}\nFlight ID: {FID}\nNumber of Seats: {num_seats}\nBooking Time: {get_current_date()}"
                            flight_details = f"\nFlight Information:\nFlight Name: {row[0]}\nDate: {row[1]}\nArrival Time: {row[5]}\nDeparture Time: {row[6]}\nNo of Stops: {row[8]}\nPrice: {row[9]}"

                            user_email = input("Enter the passenger's email address: ")
                            send_confirmation_email(user_email, sender_email, app_password, booking_details, flight_details,
                                                    user_name, user_phone, ticket_id)
                            send_thank_you_email(user_email, sender_email, app_password, is_feedback=True)

                        else:
                            print(
                                f"Not enough seats available for the requested number. Available seats: {available_seats}")
                        break

                if not found:
                    print("Invalid Flight ID or no matching flight found.")

                display_available_flights(rows, user_input1, user_input2)

        elif option == 2:
            user_input1 = input("Enter Source Station: ")
            user_input2 = input("Enter Destination: ")
            display_available_flights(rows, user_input1, user_input2)

        elif option == 3:
            user_email = input("Enter your email address: ")
            sender_password = input("Enter your email password: ")
            feedback = input("Provide your feedback: ")

            
            send_feedback_email(feedback, user_email, sender_password)
            send_thank_you_email(user_email, sender_email, app_password, is_feedback=True)


            print("Feedback sent successfully!")
        elif option == 4:
            
            ticket_id = int(input("Enter the Ticket ID to cancel: "))
            user_email = input("Enter your email address: ")  
            canceled_details = cancel_ticket(read_booked_tickets_from_file(), ticket_id, sender_email, app_password)

            if canceled_details:
                
                send_cancelation_email(user_email, sender_email, app_password, ticket_id, canceled_details)
            else:
                print("Ticket cancellation failed.")

            

        elif option == 0:
            print("Exiting the program. Goodbye!")

        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
