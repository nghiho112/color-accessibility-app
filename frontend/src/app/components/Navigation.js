'use client'

import { usePathname } from 'next/navigation';
import { Container, Nav, Navbar, SSRProvider } from 'react-bootstrap'

export default function MainMenu() {
  const pathname = usePathname();

  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="/">Color App</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link href="/" className={"/" === pathname ? "active fw-bold" : ""}>Home</Nav.Link>
            <Nav.Link href="/palette" className={"/palette" === pathname ? "active fw-bold" : ""} >Color Palette</Nav.Link>
            <Nav.Link href="/recognition" className={"/recognition" === pathname ? "active fw-bold" : ""}>Color Recognition</Nav.Link>
            <Nav.Link href="/simulator" className={"/simulator" === pathname ? "active fw-bold" : ""}>Color Simulator</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}