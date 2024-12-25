import { Session } from "next-auth";
import { JWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    user: {
      _id: string;
      email: string;
    };
  }

  interface User {
    _id: string;
    email: string;
    first_name: string;
    last_name: string;
    access_token?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    _id?: string;
    email?: string;
  }
}
