import { useEffect, useState } from "react";
import { DEFAULT_USER_ID } from "./config/env";
import { BookingPage } from "./pages/BookingPage";
import { InvoicePage } from "./pages/InvoicePage";
import { MyBookingsPage } from "./pages/MyBookingsPage";
import type { BookingResponse } from "./types/cinebook";

function parseInvoiceBookingId(pathname: string): string | null {
  const match = /^\/bookings\/([^/]+)\/?$/.exec(pathname);
  return match ? decodeURIComponent(match[1]) : null;
}

export default function App() {
  const [pathname, setPathname] = useState<string>(window.location.pathname);
  const [userId, setUserId] = useState<string>(DEFAULT_USER_ID);
  const [recentBooking, setRecentBooking] = useState<BookingResponse | null>(
    null,
  );

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navigateTo = (nextPath: string) => {
    window.history.pushState({}, "", nextPath);
    setPathname(nextPath);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const navigateToInvoice = (booking: BookingResponse) => {
    setRecentBooking(booking);
    navigateTo(`/bookings/${encodeURIComponent(booking.id)}`);
  };

  const invoiceBookingId = parseInvoiceBookingId(pathname);

  if (invoiceBookingId) {
    return (
      <InvoicePage
        bookingId={invoiceBookingId}
        initialBooking={
          recentBooking?.id === invoiceBookingId ? recentBooking : null
        }
        onNavigateHome={() => navigateTo("/")}
      />
    );
  }

  if (pathname === "/my-bookings") {
    return (
      <MyBookingsPage
        userId={userId}
        onChangeUserId={setUserId}
        onNavigateHome={() => navigateTo("/")}
        onOpenInvoice={navigateToInvoice}
      />
    );
  }

  return (
    <BookingPage
      userId={userId}
      onChangeUserId={setUserId}
      onBookingCreated={navigateToInvoice}
      onNavigateMyBookings={() => navigateTo("/my-bookings")}
    />
  );
}
