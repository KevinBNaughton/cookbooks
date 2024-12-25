import NextAuth from "next-auth";
import { authConfig } from "@/auth.config";
import Credentials from "next-auth/providers/credentials";
import { z } from "zod";
import { API_URL } from "@/app/lib/definitions";

export const { auth, handlers, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      async authorize(credentials) {
        const parsedCredentials = z
          .object({ email: z.string().email(), password: z.string().min(6) })
          .safeParse(credentials);
        if (!parsedCredentials.success) {
          throw new Error("Invalid input");
        }
        const { email, password } = parsedCredentials.data;
        try {
          // Send credentials to the backend's /api/login endpoint
          const res = await fetch(`${API_URL}/api/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
          });

          const data = await res.json();

          if (!res.ok) {
            throw new Error(data.msg || "Authentication failed.");
          }

          // Assuming the backend returns { access_token: "JWT_TOKEN", user: { ... } }
          const { access_token, user } = data;
          console.info("Access token: ", access_token);
          // Return user object along with the access_token
          return { ...user, access_token };
        } catch (error) {
          console.error("Authentication error:", error);
          throw new Error("Authentication failed.");
        }
      },
    }),
  ],
  // Configure JWT callbacks
  callbacks: {
    async jwt({ token, user }) {
      // Initial sign in
      if (user) {
        token.accessToken = user.access_token;
        token._id = user._id; // Assuming user object has an id field
        if (user.email) {
          token.email = user.email;
        }
      }
      return token;
    },
    async session({ session, token }) {
      // Include accessToken in the session
      session.accessToken = token.accessToken;
      if (token._id) {
        session.user._id = token._id;
      }
      if (token.email) {
        session.user.email = token.email;
      }
      return session;
    },
    async redirect({ baseUrl }) {
      // Customize redirection after sign in/sign out if needed
      // console.debug(`url: ${url} baseUrl: ${baseUrl}`);
      return baseUrl;
    },
  },
});
