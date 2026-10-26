// Blog lead form. Same Zapier webhook and payload shape as the homepage forms,
// so Market Updates leads land in Follow Up Boss tagged "Website - Blog".
const LEAD_WEBHOOK = "https://hooks.zapier.com/hooks/catch/29074296/41iv8as/";

document.querySelectorAll("form[data-lead]").forEach(form => {
  const err = form.querySelector(".err");
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form));
    const problems = [];
    if (!d.name.trim()) problems.push("your name");
    if (!d.phone.trim() && !d.email.trim()) problems.push("a phone number or email");
    if (problems.length) { err.textContent = "Please add " + problems.join(" and ") + " so I can reach you."; err.hidden = false; return; }
    err.hidden = true;
    if (d.website) { form.replaceChildren(); return; }
    const textOk = d.sms_consent === "yes" && d.phone.trim();
    const parts = d.name.trim().split(/\s+/);
    const lines = ["Looking to: " + d.looking_to, "From Market Updates post: " + document.title];
    if (d.address && d.address.trim()) lines.push("Property: " + d.address.trim());
    if (d.message && d.message.trim()) lines.push("Message: " + d.message.trim());
    lines.push(textOk ? "Text consent: YES, checked the texting box on " + new Date().toLocaleString("en-US", {timeZone: "America/Los_Angeles"}) + " PT" : "Text consent: NO, do not text");
    const payload = {
      first_name: parts[0], last_name: parts.slice(1).join(" "),
      email: d.email.trim(), phone: d.phone.trim(), address: (d.address || "").trim(),
      source: "roysoldquick.com",
      tags: "Website - Blog, Website - " + d.looking_to,
      summary: lines.join("\n"), page: location.href
    };
    try { await fetch(LEAD_WEBHOOK, {method:"POST", mode:"no-cors", body: new URLSearchParams(payload)}); } catch (_) {}
    const box = document.createElement("div");
    box.className = "thanks";
    box.setAttribute("role", "status");
    box.innerHTML = "<h3></h3><p></p>";
    box.querySelector("h3").textContent = "Thank you, " + parts[0] + ".";
    box.querySelector("p").textContent = "Your message is on its way. I'll contact you shortly. — Roy";
    form.replaceChildren(box);
  });
});
